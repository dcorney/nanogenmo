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


def load():
    mcW = mc.MarkovChain(order=3)
    tl = text_loader.TextLoader(mcW)
    t0 = time.perf_counter()
    for fnum in range(160, 200):
        tl.import_file_s3(str(fnum))
    t1 = time.perf_counter()
    print("Import/tokenizer total time: %.3f seconds" % (t1-t0))


def make_random(mcW,n=3):
        # print("\nSome postitve-scoring sentences:")
    for i in range(n):
        score = -1
        while score < 0:
            seq = mcW.generate_sentence(mcW.random_entry())
            s = Sentence.Sentence(seq)
            score = s._score
        s.display()


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
    parser.add_argument("--deleteredis", action='store_true',help="Delete entire REDIS index - CAREFUL!")
    parser.add_argument("--random", type=int,help="Generate some random sentences")
    parser.add_argument("--load", action='store_true',help="Generate some random sentences")
    args = parser.parse_args()
    if args.deleteredis:
        mcW = mc.MarkovChain(order=3)
        mcW.delete_all_in_redis_careful()
        exit
    if args.random:
        mcW = mc.MarkovChain(order=3)
        # seq = mcW.generate_sentence(mcW.random_entry())
        # s = Sentence.Sentence(seq)
        # s.display()
        make_random(mcW, args.random)
        exit
    if args.load:
        load()
        exit

    #main()


