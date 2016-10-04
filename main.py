import markovchain as mc
import Sentence
import paragraphs


def main():
    # path = '/Users/dcorney/Documents/books/'

    mcW = mc.MarkovChain(order=3)
    # mcW.import_all(path)
    seq = mcW.generate_sentence(mcW.random_entry())
    # res = sentences.form_sentence(seq)

    print("Example sentence:")
    s = Sentence.Sentence(seq)
    # print(res)
    s.display()

    print("Three postitve-scoring sentences:")
    for i in range(3):
        score = -1
        while score < 0:
            seq = mcW.generate_sentence(mcW.random_entry())
            s = Sentence.Sentence(seq)
            score = s._score
        s.display()

    print("Paragraph from 3 seeds:")
    seq = [["the", "cat", "was"], ["the", "man", "was"], ["if", "only", "once"]]
    p =  paragraphs.seq_to_para(seq,mcW)
    print(p)


if __name__ == '__main__':
    main()
