from collections import defaultdict
from numpy import cumsum, sum, searchsorted
from util import START_TOKEN, END_TOKEN
import tokenizer_spacy as tokenizers
import os
import s3_utils
import re

# TODO: maybe pass in tokenizers class as a parameter? So can switch betwen sPacy and Stanford from calling fn.?
# TODO: store list of flies loaded into Markov model (in Redis or wherever) so we can prevent double-loading texts


class TextLoader(object):
    """Train bi-directional Markov chain over sequences of tokens.
    Then generate new sequences."""

    def __init__(self, model):
        self._model = model

    @staticmethod
    def load_file(filename):
        "Deprecated - use only on pre-trimmed texts via gutenburg_utils"
        with open(filename, 'r', errors='ignore') as myfile:
            in_text = myfile.read().replace('\n', ' ')
        header = in_text[0:2000]
        matches = re.search("language: English", header)
        if matches and (matches.group().find("English") < 0):
            trimmed = ""    # skip this article entirely
        else:
            print(filename)
            start_point = max(0, in_text.find(
                "*** START OF THIS PROJECT GUTENBERG EBOOK"))
            if start_point > 0:
                start_point += len("*** START OF THIS PROJECT GUTENBERG EBOOK")
            end_point = min(len(in_text), in_text.find(
                "*** END OF THIS PROJECT GUTENBERG EBOOK"))
            trimmed = in_text[start_point:end_point]
        return trimmed

    def import_file_simple(self, filename):
        '''
        Ignores language, encoding, trimming headers etc.
        '''
        with open(filename, 'r') as myfile:
            in_text = myfile.read().replace('\n', ' ')
        print(filename)
        print(in_text[0:100])
        self._model.train_words(tokenizers.tokenize(in_text))

    def import_file_s3(self, key_number):
        '''
        Downloads pre-trimmed from from S3 to tmp, then
        reads text locally.
        '''
        filename = "/Users/dcorney/temp/" + key_number + ".txt"
        print(filename)
        s3_utils.from_s3(key_number, filename)
        try:
            with open(filename, 'r') as myfile:
                in_text = myfile.read().replace('\n', ' ')
        except:
            in_text = ""
        if len(in_text) < 200:
            print('No text found in ' + filename)
            return
        tokens_entities = tokenizers.tokenize(in_text)
        self._model.train_words(tokens_entities['tokens'])
        self._model.append_ner(tokens_entities['entities'])

    def unimport_file_s3(self, key_number):
        '''
        Downloads pre-trimmed from from S3 to tmp, then
        reads text locally. Removes words from dictionary
        '''
        filename = "/Users/dcorney/temp/" + key_number + ".txt"
        print("Removing " + filename)
        s3_utils.from_s3(key_number, filename)
        try:
            with open(filename, 'r') as myfile:
                in_text = myfile.read().replace('\n', ' ')
        except:
            in_text = ""
        if len(in_text) < 200:
            print('No text found in ' + filename)
            return
        tokens_entities = tokenizers.tokenize(in_text)
        self._model.train_words(tokens_entities['tokens'], -1)
        self._model.unappend_ner(tokens_entities['entities'])


    def import_file(self, filename):
        trimmed_text = TextLoader.load_file(filename)
        self._model.train_words(tokenizers.tokenize(trimmed_text))

    def import_all(self, path):
        for file in os.listdir(path):
            if file.endswith(".txt"):
                self.import_file(path + file)
