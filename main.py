import markovchain as mc
import Sentence
import paragraphs
import random


def main():
    mcW = mc.MarkovChain(order=3)
    # path = '/Users/dcorney/Documents/books/'
    # mcW.import_all(path)

    # print("\nThree postitve-scoring sentences:")
    # for i in range(3):
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

    #print("\nParagraphs from wikipedia scraping...")
    # TODO replace this with a string of nouns/verbs using POS tagger, from
    # some other source...
    phrase = "London home travel danger journey return safe London"
    for word in phrase.split(" "):
        seeds = paragraphs.phrases_from_wiki(word, 3, random.randint(3, 8))
        p = paragraphs.phrases_to_para(seeds, mcW)
        print("  " + p)


if __name__ == '__main__':
    main()
