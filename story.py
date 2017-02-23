import paragraphs
import random
from time import gmtime, strftime


_site_posts_path = "/Users/dcorney/github/dc/dcorney.aws/_posts/"

_places = ["London", "Paris", "New York",
           "Timbuktu", "Coventry", "Old Kent Road"]
_journey = ["flight", "running", "walking", "car", "train"]


def phrase():
    home = random.choice(_places)
    trip1 = random.choice(_journey)
    away = random.choice(_places)
    trip2 = random.choice(_journey)
    return str.join(",", [home, trip1, away, trip2, home])


def preamble(title, phrase):
    preamble = "---\nlayout: nanogenmo-post\ncategory: auto\ntitle: " + title
    preamble += "\n---\n\n<i>\nPreamble:\nSeed phrase: \"" + phrase + "\"\n</i>\n\n"
    return preamble


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
