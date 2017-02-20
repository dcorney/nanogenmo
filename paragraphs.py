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
    wiki_titles = wikipedia.search(query, results=10)
    # if it returns a disambiguation page, then pick a link at random...
    idx = 0

    while idx < len(wiki_titles) - 1 and wiki_titles[idx].find("disambiguation") >= 0:
        idx += 1

    # Problem: summary() sometimes fails. So need a clause
    # that returns *something* - random page?
    wiki_title = wiki_titles[idx]
    try:
        try:
            #  print(wiki_title)
            text = wikipedia.summary(wiki_title)
        except wikipedia.exceptions.DisambiguationError as err:
            disambig_count = len(err.options)
            if disambig_count == 0:
                random_page = wikipedia.random(1)
                # print("Nothing found! So.. " + random_page)
                text = wikipedia.summary(random_page)
            else:
                links = [x for x in err.options if x.find(
                    "disambiguation") < 0]
                random_page = links[random.randint(0, len(links) - 1)]
                # print("Many found! Chose: " + random_page)
                text = wikipedia.summary(random_page)
                # stext = wiki_text(random_page)
    except:
        random_page = wikipedia.random(1)
        text = wikipedia.summary(random_page)

    return(text)


def phrase_from_sentence(sentence, n):
    """
    Pick a random sequence of words from a sentence
    """
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    start = random.randint(0, max(0, (len(tokens) - n)))
    phrase_tokens = tokens[start:start + n]
    return(" ".join(phrase_tokens))


def phrases_from_wiki(query, phrase_length, max_phrases=50):
    """
    Get text from wikipedia; then for each sentence, return a
    sequnence of words.
    """
    text = wiki_text(query)
    sents = nltk.sent_tokenize(text)
    all_phrases = [phrase_from_sentence(s, phrase_length) for s in sents]
    return (all_phrases[0:min(max_phrases, len(all_phrases) - 1)])


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


def scored_sentence(seed, mc):
    score = -1
    attempts = 5
    while score < 0 and attempts > 0:
        seq = mc.generate_sentence(seed)
        s = Sentence.Sentence(seq)
        score = s._score
        attempts -= 1
    return s


def phrases_to_para(phrases, mc):
    para = ""
    for phrase in phrases:
        seed = phrase.split(" ")
        # tokens = mc.generate_sentence(seed)
        # s = Sentence.Sentence(tokens)
        s = scored_sentence(seed, mc)
        para += s.get_text() + "  "
    return para

# defn text->seq - takes a block of text and produces a sequence of seeds
# of a given model size

# defn wiki->text (different module?)
