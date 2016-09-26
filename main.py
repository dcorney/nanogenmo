import markovchain as mc
import sentences


def main():
    path = '/Users/dcorney/Documents/books/'
    mcW = mc.MarkovChain(order=2)
    mcW.import_all(path, mcW)

    seq = mcW.generate_sentence(mcW.random_entry()[0].split("|"))
    # res = sentences.form_sentence(seq)
    s = sentences.sentences()
    res = s.form_sentence(seq)
    #print(res)
    s.display()

if __name__ == '__main__':
    main()
