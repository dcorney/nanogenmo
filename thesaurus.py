from nltk.corpus import wordnet as wn
import random


def synonym(word):
    all_synsets = wn.synsets(word)
    if not all_synsets: return word
    synset = all_synsets[0]  # random.choice(all_synsets)
    terms = [t for h in synset.hyponyms() for t in h.lemmas()]
    if terms:
        lemma = random.choice(terms)
        synonym = lemma.name()
    else:
        terms = synset.lemma_names()
        if not terms: return word
        synonym = random.choice(terms)
    return(synonym.replace("_", " "))


def expand_seeds(init_list, n=10):
    "Take a list of words and return a list of n words, including\
    repetitions and synonyms etc. of the originals"
    seeds = []
    for i in range(0, n):
        idx = i * len(init_list) // n
        term = init_list[idx]
        if random.random() < 0.5:
            term = synonym(term)
        seeds.append(term)
    return(seeds)

    # See http://www.nltk.org/howto/wordnet.html
    # e.g. synset.defintion()


if __name__ == '__main__':
    print(expand_seeds(["cat", "dog", "fish"], 10))
