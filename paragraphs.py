import Sentence


def seq_to_para(seq,mc):
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

# defn text->seq - takes a block of text and produces a sequence of seeds
# of a given model size

# defn wiki->text (different module?)
