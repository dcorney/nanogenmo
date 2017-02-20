from collections import defaultdict
import random
from numpy import cumsum, sum, searchsorted
from numpy.random import rand
from util import START_TOKEN, END_TOKEN
import tokenizers
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
        self._ner_sf = {"ORGANIZATION": [], "PERSON": [], "LOCATION": []}

    def delete_all_in_redis_careful(self):
        self._redis.flushdb()

    # TODO: build multiple models at once.
    # Or just n words with n-1 separators. But store all when training, and
    # replace 'order' with 'max-order'
    def train_words(self, sequence):
        win_size = 3
        for idx in range(len(sequence)):
            start = max(0, idx - win_size)
            end = idx
            for sub_idx in range(start, end):
                node_from = '|'.join(sequence[sub_idx:end]) + ":fwd"
                node_to = str(sequence[idx])
                # print(node_from + " -> " + node_to)
                self._redis.hincrby(node_from, node_to, 1)
            start = idx + 1
            end = min(idx + win_size + 1, len(sequence))
            for sub_idx in range(start + 1, end + 1):
                node_from = '|'.join(sequence[start:sub_idx]) + ":back"
                node_to = str(sequence[idx])
                # print(node_from + " -> " + node_to)
                self._redis.hincrby(node_from, node_to, 1)

    def append_ner(self, entities):
        self._ner_sf['ORGANIZATION'] += entities['ORGANIZATION']
        self._ner_sf['PERSON'] += entities['PERSON']
        self._ner_sf['LOCATION'] += entities['LOCATION']

    def ner_report(self, n=5):
        print(self._ner_sf['PERSON'][0:n])
        print(self._ner_sf['ORGANIZATION'][0:n])
        print(self._ner_sf['LOCATION'][0:n])

    def train_words_OLD(self, sequence):
        """
        Trains the model using sequence of words.
        """
        self._symbols.extend(list(set(sequence)))
        for i in range(len(sequence) - self._order):
            node_from = '|'.join(sequence[i:i + self._order]) + ":fwd"
            node_to = sequence[i + self._order]
            self._redis.hincrby(node_from, node_to, 1)
            r_node_from = '|'.join(
                sequence[i + 1:i + self._order + 1]) + ":back"
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
                probs = self._redis.hgetall(self._redis.randomkey())
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
        return list(probs.keys())[idx].decode("utf-8")

    def random_entry(self):
        s = self._redis.randomkey().decode("utf-8")
        return s[0:s.rfind(":")].split("|")

    def fill_sf(self, token):
        if token == '<PERSON>':
            return random.choice(self._ner_sf['PERSON'])
        if token == '<ORGANIZATION>':
            return random.choice(self._ner_sf['ORGANIZATION'])
        if token == '<LOCATION>':
            return random.choice(self._ner_sf['LOCATION'])
        return token

    def polish_sentence(self, sentence):
        polished = [self.fill_sf(t) for t in sentence]
        return polished

    def generate_sentence(self, start):
        """
        Uses seed token-list as 'middle' of new sentence, growing it
        until it starts & ends with 'end' tokens
        """
        result = list(start)  # make a copy of start so we don't mutate it
        while result[-1] != END_TOKEN:
            new = self.predict(result[-self._order:])
            result.append(new)
        while result[0] != START_TOKEN:
            new = self.predict(result[0:self._order], direction='reverse')
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
