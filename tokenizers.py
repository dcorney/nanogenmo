#import nltk
from nltk import word_tokenize,sent_tokenize
from util import START_TOKEN, END_TOKEN


def tokenize_sentence(s):
    tk_list = word_tokenize(s)
    tk_list.insert(0, START_TOKEN)
    tk_list.append(END_TOKEN)
    return tk_list


def tokenize(text):
    """
    Split text into sentences; then split sentences into tokens.
    """
    sents = sent_tokenize(text)
    all_tokens = [tokenize_sentence(s) for s in sents]
    return [item for sublist in all_tokens for item in sublist]
