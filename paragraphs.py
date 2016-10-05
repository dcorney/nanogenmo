import Sentence
import wikipedia
import nltk
# from nltk.tag import StanfordNERTagger
from nltk.tokenize import RegexpTokenizer
import random


def wiki_text(query):
    """
    Get text from Wikipedia
    """
    wiki_title = wikipedia.search(query, results=1)
    # TODO: try/catch: if it returns a disambiguation page, then pick a link
    # at random...
    text = wikipedia.summary(wiki_title)
    return(text)


def phrase_from_sentence(sentence, n):
    """
    Pick a random sequence of words from a sentence
    """
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    start = random.randint(0, (len(tokens) - n))
    phrase_tokens = tokens[start:start + n]
    return(" ".join(phrase_tokens))


def phrases_from_wiki(query, phrase_length):
    """
    Get text from wikipedia; then for each sentence, return a
    sequnence of words.
    """
    text = wiki_text(query)
    sents = nltk.sent_tokenize(text)
    all_phrases = [phrase_from_sentence(s, phrase_length) for s in sents]
    return (all_phrases)


def seq_to_para(seq, mc):
    """
    takes a sequence of seeds & returns one sentence each,
    formed into a paragraph.
    """
    para = ""
    for seed in seq:
        tokens = mc.generate_sentence(seed)
        s = Sentence.Sentence(tokens)
        para += s.get_text() + "  "
    return para


def phrases_to_para(phrases, mc):
    para = ""
    for phrase in phrases:
        seed = phrase.split(" ")
        tokens = mc.generate_sentence(seed)
        s = Sentence.Sentence(tokens)
        para += s.get_text() + "  "
    return para

# defn text->seq - takes a block of text and produces a sequence of seeds
# of a given model size

# defn wiki->text (different module?)
