import markovchain as mc
import Sentence
import paragraphs
import random
import text_loader
import story
from timeit import default_timer as timer
import gutenburg_utils as guten


def test():
    mcW = mc.MarkovChain(order=3)
    # mcW.delete_all_in_redis_careful()
    tl = text_loader.TextLoader(mcW)
    tmp_file = "/tmp/guten.txt"
    for fnum in range(101, 110):
        guten.from_s3(str(fnum), tmp_file)
        tl.import_file_SIMPLE(tmp_file)
    seq = mcW.generate_sentence(mcW.random_entry())
    s = Sentence.Sentence(seq)
    s.display()


def main():
    start = timer()
    mcW = mc.MarkovChain(order=3)
    # mcW.delete_all_in_redis_careful()
    tl = text_loader.TextLoader(mcW)
    tl.import_file_s3("155")
    tl.import_file_s3("171")
    tl.import_file_s3("174")
    tl.import_file_s3("204")
    tl.import_file_s3("205")
    # mcW.ner_report()
    # path = '/Users/dcorney/Documents/books/'
    # tl.import_all(path)

    # print("\nSome postitve-scoring sentences:")
    # for i in range(5):
    #     score = -1
    #     while score < 0:
    #         seq = mcW.generate_sentence(mcW.random_entry())
    #         s = Sentence.Sentence(seq)
    #         score = s._score
    #     s.display()

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
    main()
