from collections import defaultdict
from numpy import cumsum, sum, searchsorted
from numpy.random import rand

class MarkovChain(object):
	"""Train bi-directional Markov chain over sequences of tokens. 
	Then generate new sequences."""

	START_TOKEN = "<SENTENCE_START>"
	END_TOKEN = "<SENTENCE_END>"

	def __init__ (self, order):
		self._order = order
		self._transitions = defaultdict(int)
		self._reverse_transitions = defaultdict(int)
		self._symbols = []
 
	def train_words(self, sequence):
		"""
		Trains the model using sequence of words.
		"""
		self._symbols.extend( list(set(sequence)))
		for i in range(len(sequence)-self._order):
			node_from = '|'.join(sequence[i:i+self._order])
			node_to = sequence[i+self._order]
			self._transitions[node_from,node_to] += 1
			r_node_from = '|'.join(sequence[i+1:i+self._order+1])
			r_node_to = sequence[i]
			self._reverse_transitions[r_node_from,r_node_to] += 1

	def predict(self, symbols, direction='forward'):
		"""
		Takes in input a list of words and predicts the next word.
		"""
		#if len(symbol) != self._order:
		#    raise ValueError('Expected string of %d chars, got %d' % (self._order, len(symbol)))
		node_from = '|'.join(symbols)
		if direction=='reverse':
			probs = [self._reverse_transitions[(node_from, s)] for s in self._symbols]
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
			new = self.predict(start,direction='reverse')
			result.insert(0,new)
			start = result[0:self._order]
		return result

	def generate_sentence(self,start):
		"""
		Uses seed as 'middle' of new sentence, growing it until it starts & 
		ends with 'end' tokens
		"""
		result = start
		while result[-1] != END_TOKEN:
			new = self.predict(start)
			result.append(new)
			start = result[-self._order:]
		start = result[0:self._order]
		while result[0] != START_TOKEN :
			new = self.predict(start, direction='reverse')
			result.insert(0,new)
			start = result[0:self._order]
		return result
	
		
	@staticmethod
	def _weighted_pick(weights):
		"""
		  Weighted random selection returns n_picks random indexes.
		  The chance to pick the index i is given by weights[i].
		"""
		return searchsorted(cumsum(weights), rand()*sum(weights))