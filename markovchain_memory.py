from collections import defaultdict
import random
from numpy import cumsum, sum, searchsorted
from numpy.random import rand
from util import START_TOKEN, END_TOKEN
import tokenizers
import os

# Stores transitions in memory
# See also markovchain: stores transition probabilities in a persistent DB


class MarkovChain(object):
    """Train bi-directional Markov chain over sequences of tokens.
    Then generate new sequences."""

    def __init__(self, order):
        self._order = order
        self._transitions = defaultdict(int)
        self._reverse_transitions = defaultdict(int)
        self._symbols = []

    def train_words(self, sequence):
        """
        Trains the model using sequence of words.
        """
        self._symbols.extend(list(set(sequence)))
        for i in range(len(sequence) - self._order):
            node_from = '|'.join(sequence[i:i + self._order])
            node_to = sequence[i + self._order]
            self._transitions[node_from, node_to] += 1
            r_node_from = '|'.join(sequence[i + 1:i + self._order + 1])
            r_node_to = sequence[i]
            self._reverse_transitions[r_node_from, r_node_to] += 1

    def import_file(self, filename, mc):
        with open(filename, 'r') as myfile:
            in_text = myfile.read().replace('\n', ' ')
        start_point = max(0, in_text.find("*** START OF THIS PROJECT GUTENBERG EBOOK"))
        if start_point > 0:
            start_point += len("*** START OF THIS PROJECT GUTENBERG EBOOK")
        end_point = min(len(in_text), in_text.find("*** END OF THIS PROJECT GUTENBERG EBOOK"))
        trimmed = in_text[start_point:end_point]
        # mc.train_words(in_text.split())
        self.train_words(tokenizers.tokenize(trimmed))

    def import_all(self, path, mc):
        for file in os.listdir(path):
            if file.endswith(".txt"):
                self.import_file(path + file, mc)

    def predict(self, symbols, direction='forward'):
        """
        Takes in input a list of words and predicts the next word.
        """
        # if len(symbol) != self._order:
        #    raise ValueError('Expected string of %d chars, got %d' % (self._order, len(symbol)))
        node_from = '|'.join(symbols)
        if direction == 'reverse':
            probs = [self._reverse_transitions[
                (node_from, s)] for s in self._symbols]
        else:
            probs = [self._transitions[(node_from, s)] for s in self._symbols]
        return self._symbols[self._weighted_pick(probs)]

    def random_entry(self):
        return random.choice(list(self._transitions.keys()))

    def generate(self, start, n):
        """
        Generates n words from start.
        """
        result = start
        for i in range(n):
            new = self.predict(start)
            result.append(new)
            start = result[-self._order:]
        return result

    def generate_reverse(self, start, n):
        """
        Generates n words from start.
        """
        result = start
        for i in range(n):
            new = self.predict(start, direction='reverse')
            result.insert(0, new)
            start = result[0:self._order]
        return result

	    def generate_sentence(self, start):
	        """
	        Uses seed token-list as 'middle' of new sentence, growing it
	        until it starts & ends with 'end' tokens
	        """
	        result = start
	        while result[-1] != END_TOKEN:
	            new = self.predict(start)
	            result.append(new)
	            start = result[-self._order:]
	        start = result[0:self._order]
	        while result[0] != START_TOKEN:
	            new = self.predict(start, direction='reverse')
	            result.insert(0, new)
	            start = result[0:self._order]
	        return result

    @staticmethod
    def _weighted_pick(weights):
        """
          Weighted random selection returns n_picks random indexes.
          The chance to pick the index i is given by weights[i].
        """
        return searchsorted(cumsum(weights), rand() * sum(weights))
