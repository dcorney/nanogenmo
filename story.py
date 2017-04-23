import paragraphs
import random
from time import gmtime, strftime
import markov_dialogue as dialogue
import thesaurus


_site_posts_path = "/Users/dcorney/github/dc/dcorney.aws/_posts/"

_places = ["London", "Paris", "New York",
           "Timbuktu", "Coventry", "Old Kent Road"]
_journey = ["flight", "running", "walking", "car", "train"]


def random_phrase_static():
    home = random.choice(_places)
    trip1 = random.choice(_journey)
    away = random.choice(_places)
    trip2 = random.choice(_journey)
    return str.join(",", [home, trip1, away, trip2, home])


def random_phrase(mcW):
    home = mcW.random_entity(mcW._ner_loc)
    item = mcW.random_entity(mcW._ner_org)
    # home = random.choice(_places)
    trip1 = random.choice(_journey)
    away = mcW.random_entity(mcW._ner_loc)  #= random.choice(_places)
    trip2 = random.choice(_journey)
    return str.join(",", [home, item, trip1, away, item, trip2, home])


def preamble(title, phrase):
    preamble = "---\nlayout: nanogenmo-post\ncategory: auto\ntitle: " + title
    preamble += "\n---\n\n<i>\nPreamble:\nSeed phrase: \"" + phrase + "\"\n</i>\n\n"
    return preamble


def text_to_blog(title, text):
    filename = _site_posts_path + \
        strftime("%Y-%m-%d", gmtime()) + "-" + title + ".md"
    text = text.replace("\n", "\n\n")
    blog_file = open(filename, "w")
    blog_file.write(text)
    blog_file.close()
    print ("Wrote " + str(len(text)) + " chars to " + filename)
    return filename


def phrase_to_blog(title, phrase, mcW):
    filename = _site_posts_path + \
        strftime("%Y-%m-%d", gmtime()) + "-" + title + ".md"
    story = preamble(title, phrase)
    for word in phrase.split(","):
        seeds = paragraphs.phrases_from_wiki(word, 3, random.randint(3, 10))
        p = paragraphs.phrases_to_para(seeds, mcW)
        story = story + "<p>" + p + "</p>\n\n"
    blog_file = open(filename, "w")
    blog_file.write(story)
    blog_file.close()
    print ("Wrote " + str(len(story)) + " chars to " + filename)
    return story


def make_dialogue_block(mcW):
    "Make a whole block. First & last seed-words generate intro; then introduce some\
    speakers, then those speakers with those seed-words for actual dialogue; then\
    a prose epilogue of the people & the last seed-word."
    # phrase = "London dog dog dog safe cat cat travel train train train ship ship ship \
    # danger death death death murder rescue return return return safe London London London"
    story = ""
    seed_phrase = random_phrase(mcW)  # "city train dog cat dog"
    init_seeds = seed_phrase.split(",")
    p_seeds = paragraphs.phrases_to_para(init_seeds[::len(init_seeds) - 1], mcW)  # Intro = first & last terms

    full_cast = []
    for i in range(0, 10):
        full_cast.append(mcW.random_entity(mcW._ner_per))
    people = full_cast[0:2]
    random.shuffle(people)
    p_people = paragraphs.phrases_to_para(people, mcW)

    story += "  " + p_seeds + "\n " + p_people + "\n"

    seeds = thesaurus.expand_seeds(init_seeds, 20)
    dm = dialogue.dialogue_maker(people, ["he", "he", "she", "he"], mcW, seeds)
    story += dm.make_dialogue()

    people = full_cast[0:3]
    random.shuffle(people)
    p = paragraphs.phrases_to_para(people + list(seeds[-1]), mcW)
    story += "  " + p + "\n"

    seeds = thesaurus.expand_seeds(init_seeds, 20)
    dm = dialogue.dialogue_maker(people, ["he", "he", "she", "he"], mcW, seeds)
    story += dm.make_dialogue()

    p = paragraphs.phrases_to_para(people + list(seeds[-1]), mcW)
    story += "  " + p + "\n"

    print(story)
    return story
