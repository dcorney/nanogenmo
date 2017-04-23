from collections import defaultdict
import random
from numpy import cumsum, sum, searchsorted
from numpy.random import rand
from util import START_TOKEN, END_TOKEN
import os
import redis
import re


class MarkovChain(object):
    """Train bi-directional Markov chain over sequences of tokens.
    Then generate new sequences."""

    def __init__(self, order):
        self._order = order
        self._redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._symbols = []
        self._ner_per = "PERSON"
        self._ner_org = "ORGANIZATION"
        self._ner_loc = "LOCATION"
        self._verbosity = 0

    def delete_all_in_redis_careful(self):
        self._redis.flushdb()

    # TODO: build multiple models at once.
    # Or just n words with n-1 separators. But store all when training, and
    # replace 'order' with 'max-order'
    def train_words(self, sequence, weight=1):
        win_size = 3
        for idx in range(len(sequence)):
            start = max(0, idx - win_size)
            end = idx
            for sub_idx in range(start, end):
                node_from = '|'.join(sequence[sub_idx:end]) + ":fwd"
                node_to = str(sequence[idx])
                if self._verbosity > 10: print(node_from + " -fwd> " + node_to)
                new_val = self._redis.hincrby(node_from, node_to, weight)
                if new_val <= 0:
                    self._redis.hdel(node_from, node_to)
            start = idx + 1
            end = min(idx + win_size + 1, len(sequence))
            for sub_idx in range(start + 1, end + 1):
                node_from = '|'.join(sequence[start:sub_idx]) + ":back"
                node_to = str(sequence[idx])
                if self._verbosity > 10:  print(node_from + " -back> " + node_to)
                new_val = self._redis.hincrby(node_from, node_to, weight)
                if new_val <= 0:
                    self._redis.hdel(node_from, node_to)

    def append_ner(self, entities):
        for ner_type in [self._ner_per, self._ner_org, self._ner_loc]:
            for entity in entities[ner_type]:
                self._redis.rpush(ner_type, entity)

    def unappend_ner(self, entities):
        "Remove one copy of each entity in the list"
        for ner_type in [self._ner_per, self._ner_org, self._ner_loc]:
            for entity in entities[ner_type]:
                self._redis.lrem(ner_type, 1, entity)

    def ner_report(self, n=2):
        print(self._redis.lrange(self._ner_per, 0, n))
        print(self._redis.lrange(self._ner_org, 0, n))
        print(self._redis.lrange(self._ner_loc, 0, n))

    def train_words_OLD(self, sequence):
        """
        Trains the model using sequence of words.
        """
        self._symbols.extend(list(set(sequence)))
        for i in range(len(sequence) - self._order):
            node_from = '|'.join(sequence[i:i + self._order]) + ":fwd"
            node_to = sequence[i + self._order]
            self._redis.hincrby(node_from, node_to, 1)
            r_node_from = '|'.join(sequence[i + 1:i + self._order + 1]) + ":back"
            r_node_to = sequence[i]
            self._redis.hincrby(r_node_from, r_node_to, 1)

    def get_probs(self, sequence, direction='forward'):
        node_from = '|'.join(sequence)
        if direction == 'reverse':
            probs = self._redis.hgetall(node_from + ":back")
        else:
            probs = self._redis.hgetall(node_from + ":fwd")
        if (len(probs) == 0):
            if len(sequence) == 0:
                #TODO: should be :back half the time:
                while (len(probs) == 0):
                    # TODO: not sure why this bit is needed... how can a random-entry have no probs?
                    e = self.random_entry()
                    probs = self._redis.hgetall('|'.join(e) + ":fwd")
            else:
                if direction == 'reverse':
                    sub_seq = sequence[0:-1]
                else:
                    sub_seq = sequence[1:]
                probs = self.get_probs(sub_seq, direction)
        return probs

    def predict(self, sequence, direction='forward'):
        """
        Takes in input a list of words and predicts the next word.
        """
        probs = self.get_probs(sequence, direction)
        weights = [int(x) for x in list(probs.values())]
        idx = searchsorted(cumsum(weights), rand() * sum(weights))
        if self._verbosity > 10: print("Predicting from '" + str(sequence) + "' with " + str(len(probs)) + " probs")
        if self._verbosity > 15: print("idx=" + str(idx) + " len(probs)=" + (str(len(probs.keys()))) + " " + str(list(probs)[0]))
        return list(probs.keys())[idx].decode("utf-8")

    def random_entry(self):
        "Make sure random entry is not a special token (e.g. sentence-start)"
        while True:
            s = self._redis.randomkey().decode("utf-8")
            if not(s.startswith(START_TOKEN) or s.startswith(END_TOKEN)):
                break
        return s[0:s.rfind(":")].split("|")

    def random_entity(self, ner_type):
        # if token == '<PERSON>':
        #     idx = random.randint(0, self._redis.llen(self._ner_per) - 1)
        #     return self._redis.lindex(self._ner_per, idx).decode('UTF-8')
        # if token == '<ORGANIZATION>':
        #     idx = random.randint(0, self._redis.llen(self._ner_org) - 1)
        #     return self._redis.lindex(self._ner_org, idx).decode('UTF-8')
        # if token == '<LOCATION>':
        #     idx = random.randint(0, self._redis.llen(self._ner_loc) - 1)
        #     return self._redis.lindex(self._ner_loc, idx).decode('UTF-8')
        # return token
        idx = random.randint(0, self._redis.llen(ner_type) - 1)
        return self._redis.lindex(ner_type, idx).decode('UTF-8')


    def surface_forms(self, token):
        if token[1:-1] == self._ner_loc or token[1:-1] == self._ner_org or token[1:-1] == self._ner_per:
            return(self.random_entity(token[1:-1]))
        else:
            return token

    def polish_sentence(self, sentence):
        polished = [self.surface_forms(t) for t in sentence]
        return polished

    def generate_sentence(self, start):
        """
        Uses seed token-list as 'middle' of new sentence, growing it
        until it starts & ends with 'end' tokens
        """
        result = list(start)  # make a copy of start so we don't mutate it
        while result[-1] != END_TOKEN:
            new = self.predict(result[-self._order:])
            if self._verbosity > 10: print("Generate fwd from " + str(result[0:self._order]) + " to " + new)
            result.append(new)
        while result[0] != START_TOKEN:
            new = self.predict(result[0:self._order], direction='reverse')

            if self._verbosity > 10: print("Generate reverse from " + str(result[0:self._order]) + " to " + new)
            result.insert(0, new)
        result = self.polish_sentence(result)
        return result

    @staticmethod
    def _weighted_pick(weights):
        """
          Weighted random selection returns n_picks random indexes.
          The chance to pick the index i is given by weights[i].
        """
        return searchsorted(cumsum(weights), rand() * sum(weights))


def test():
    mcW = MarkovChain(order=3)
    mcW._verbosity = 100
    print(mcW.random_entity(mcW._ner_per))
    #r = mcW.generate_sentence(["this","man"])
    #print(r)

if __name__ == '__main__':
    test()

