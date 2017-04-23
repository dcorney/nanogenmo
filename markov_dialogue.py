import numpy as np
from numpy import cumsum, sum, searchsorted
from numpy.random import rand
import sys
import math
import paragraphs
import markovchain as mc

# TODO: make this into a class
# setters: list of speakers, pronouns, priors etc.
# random transitions
# Internal: build list of structures:
#     e.g.{:speaker_name "Alice", :speaker_pronoun "she", :speaker_str "she", :speech_verb "said", :position "end"}
# Then end with fn that maps that out to a suitable string
#     e.g. "<SPEECH>, she said."
# External bit then replaces <SPEECH> with a markov-chain-generated sentence (or several).

class dialogue_maker(object):

    def __init__(self, names, pronouns, mc, seeds):
        self.speakers = [{"name": n, "pronoun": p} for n, p in list(zip(names, pronouns))]
        self.transitions = self.make_transition_probs(self)
        self.speech_acts = ["said", "whispered", "shouted", "cried"]
        self.acts_transitions = [25, 2, 2, 2]
        self.mc = mc
        self.seeds = seeds

    def make_transition_probs(self, n):
        n = len(self.speakers)
        transitions = np.random.randint(5, size=(n, n)) + 1
        transitions += transitions.transpose()
        for i in range(0, math.floor(n / 2)):
            s1 = np.random.randint(n)
            s2 = np.random.randint(n)
            transitions[s1][s2] += 10
            transitions[s2][s1] += 8
        return(transitions)

    def after(self, speaker_id):
        row = self.transitions[speaker_id]
        sucessor = searchsorted(cumsum(row), rand() * sum(row))
        return sucessor

    def speaker_sequence(self, speaker_id, n):
        "Random walk through transitions matrix to produce a sequence of speaker ids"
        seq = []
        for i in range(n):
            seq.append(speaker_id)
            speaker_id = self.after(speaker_id)
        return seq

    def speech_sequence(self, n):
        speech_acts_seq = []
        next_speech_id = 0
        for i in range(n):
            next_speech_id = searchsorted(cumsum(self.acts_transitions), rand() * sum(self.acts_transitions))
            speech_acts_seq.append(self.speech_acts[next_speech_id])
        return speech_acts_seq

    def seq_to_names(self, sequence):
        return([self.speakers[id] for id in sequence])

    def make_speech_bits(self, n):
        seq = self.speaker_sequence(0, n)
        self.speech_acts = self.speech_sequence(n)
        return [{'speaker_name': self.speakers[seq[i]]["name"],
                 'speech_act': self.speech_acts[seq[i]],
                 'seq_id': seq[i],
                 'speech': paragraphs.scored_sentence([self.seeds[i]], self.mc),
                 'paragraph': True}
                for i in range(n)]

    def simplify(self, seq_map):
        "Take a sequence of speech parts and make more natural by removing name reptition etc."
        for i in range(0, len(seq_map)):
            seq_map[i]['speaker_str'] = seq_map[i]['speaker_name']  # default
            # Same speaker contiues:
            if i > 0 and seq_map[i]['seq_id'] == seq_map[i - 1]['seq_id']:
                seq_map[i]['speaker_str'] = ""
                seq_map[i]['speech_act'] = ""
                seq_map[i]['paragraph'] = False
            else:
                if i > 1 and seq_map[i]['seq_id'] == seq_map[i - 2]['seq_id'] \
                   and seq_map[i]['seq_id'] != seq_map[i - 1]['seq_id']:
                    seq_map[i]['speaker_str'] = ""
                    seq_map[i]['speech_act'] = ""
                    seq_map[i]['paragraph'] = True
        return seq_map

    def report_seq(self, seq_map):
        text = ""
        for i in range(0, len(seq_map)):
            if seq_map[i]['paragraph']:
                sys.stdout.write('\n    ')
                quote_start = " '"
            else:
                quote_start = ""
            if i > len(seq_map) - 2 or seq_map[i + 1]['paragraph']:
                quote_end = "'"
            else:
                quote_end = " "
            if len(seq_map[i]['speech_act']) > 0:
                speech_act = " " + seq_map[i]['speech_act'] + ","
            else:
                speech_act = seq_map[i]['speech_act']

            # sys.stdout.write(seq_map[i]['speaker_str'] + speech_act +
            #                  quote_start + seq_map[i]['speech'].get_text() + quote_end)

            text += seq_map[i]['speaker_str'] + speech_act +\
                    quote_start + seq_map[i]['speech'].get_text() + quote_end + "\n"
        return text

    def make_dialogue(self):
        n = len(self.seeds)
        acts = self.make_speech_bits(n)
        seq_map = self.simplify(acts)
        text = self.report_seq(seq_map)
        return(text)


if __name__ == '__main__':
    mcW = mc.MarkovChain(order=3)
    # print(paragraphs.scored_sentence(["safe"], mcW))

    # phrase = "London dog dog dog safe cat cat travel train train train ship ship ship \
    # danger death death death murder rescue return return return safe London London London"
    phrase = "dog cat cat dog dog dog"
    seeds = phrase.split(" ")
    dm = dialogue_maker(["Alice", "Bob", "Carol", "Dan"], ["she", "he", "she", "he"], mcW, seeds)
    dm.make_dialogue()
