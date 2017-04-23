import markovchain as mc
import Sentence
import paragraphs
import random
import text_loader
import story
import argparse
from timeit import default_timer as timer
import time
import gutenburg_utils as guten
import markov_dialogue as dialogue
import thesaurus


def load():
    mcW = mc.MarkovChain(order=3)
    tl = text_loader.TextLoader(mcW)
    t0 = time.perf_counter()
    for fnum in range(250, 300):
        tl.import_file_s3(str(fnum))
    t1 = time.perf_counter()
    print("Import/tokenizer total time: %.3f seconds" % (t1 - t0))

def unload():
    mcW = mc.MarkovChain(order=3)
    tl = text_loader.TextLoader(mcW)
    t0 = time.perf_counter()
    # bigger files: 115,180,
    for fnum in [226,227]:
        tl.unimport_file_s3(str(fnum))

    # for fnum in [101,104,106,114,118,124,127,131,227,229,230,228,231,232,247,258,277,278]:
    #      tl.unimport_file_s3(str(fnum))

    t1 = time.perf_counter()
    print("Import/tokenizer total time: %.3f seconds" % (t1 - t0))


def make_random(mcW, n=3):
    "Make some postitve-scoring sentences"
    for i in range(n):
        score = -1
        while score < 0:
            seq = mcW.generate_sentence(mcW.random_entry())
            s = Sentence.Sentence(seq)
            score = s._score
        s.display()


def make_dialoge():
    mcW = mc.MarkovChain(order=3)
    story.make_dialogue_block(mcW)


def main():
    start = timer()
    mcW = mc.MarkovChain(order=3)
    # mcW.ner_report()
    # print("\nParagraph from 3 phrases")
    # p = paragraphs.phrases_to_para(
    #     ["the cat was", "the man was", "if only once"], mcW)
    # print(p)

    # print("\nParagraphs from wikipedia")
    # seeds = paragraphs.phrases_from_wiki("London", 3, 6)
    # p = paragraphs.phrases_to_para(seeds, mcW)
    # print(p)

    # print("\nParagraphs from wikipedia scraping...")
    # TODO replace this with a string of nouns/verbs using POS tagger, from
    # some other source...
    phrase = "London safe travel train aeroplane ship danger death murder rescue return safe London"
    for word in phrase.split(" "):
        seeds = paragraphs.phrases_from_wiki(word, 3, random.randint(3, 10))
        p = paragraphs.phrases_to_para(seeds, mcW)
        print("  " + p)
    # story.phrase_to_blog("test_NER1", story.phrase(), mcW)
    end = timer()
    print('Total elapsed time:')
    print(end - start)  


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--deleteredis", action='store_true',help="Delete entire Redis index - CAREFUL!")
    parser.add_argument("--random", type=int,help="Generate some random sentences")
    parser.add_argument("--load", action='store_true',help="Load more texts into Markov-model")
    parser.add_argument("--unload", action='store_true',help="Remove some texts from Markov-model")
    parser.add_argument("--dialogue", action='store_true',help="Make some dialogue")
    args = parser.parse_args()
    if args.deleteredis:
        mcW = mc.MarkovChain(order=3)
        mcW.delete_all_in_redis_careful()
        exit
    if args.random:
        mcW = mc.MarkovChain(order=3)
        make_random(mcW, args.random)
        exit
    if args.load:
        load()
        exit
    if args.unload:
        unload()
        exit
    if args.dialogue:
        make_dialoge()
        exit


