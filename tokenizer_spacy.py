from spacy.en import English
import itertools
from util import START_TOKEN, END_TOKEN
import re
import string

nlp = English()

# Create anonymous class instance to wrap boundary token as a non-entity token
start_obj = type('fake_token', (object,), {"text": START_TOKEN, "ent_iob_": 'O', "idx":-1})
end_obj = type('fake_token', (object,), {"text": END_TOKEN, "ent_iob_": 'O', "idx":-1})


def type_lookup(ent_type):
    index = {"GPE": "LOCATION", "LOC": "LOCATION", "ORG": "ORGANIZATION"}
    return(index.get(ent_type, ent_type))


def sentence_boundaries(sentence):
    tokens = [token for token in sentence]
    tokens.insert(0, start_obj)
    tokens.append(end_obj)

    # print("\nNew sentence " + str(tokens[1].idx))
    # print(sentence)
    return tokens


def doc_to_types(doc):
    ents = list(doc.ents)
    data = sorted(ents, key=lambda x: x.label_)
    groups = itertools.groupby(data, lambda x: x.label_)

    all_groups = []
    uniquekeys = []
    for k, g in groups:
        all_groups.append(list(g))      # Store group iterator as a list
        uniquekeys.append(k)
    # See https://spacy.io/docs/usage/entity-recognition for all types
    # E.g. 'NORP' = nationality/religion/political grp
    # FACILITY, PRODUCT, LANGUAGE, LOC (other locations; GPE=cities, countries etc.)
    examples = {"PERSON": all_groups[uniquekeys.index('PERSON')] if 'PERSON' in uniquekeys else [],
                "LOCATION": all_groups[uniquekeys.index('GPE')] if 'GPE' in uniquekeys else [],
                "ORGANIZATION": all_groups[uniquekeys.index('ORG')] if 'ORG' in uniquekeys else []}
    #print(examples["PERSON"][0:5])
    return examples


def is_plain_token(token):
    if token.ent_iob_ == 'O':
        return True
    ttype = token.ent_type_.upper()
    if ttype == "PERSON" or ttype == "LOCATION" or ttype == "ORGANIZATION":
        return False
    return True


def tokenize(text):
    pattern = re.compile('[^\w_ ,\.\';:!?]+')  # hack to remove quote-marks etc. which can confuse sentence tokenizer
    text = pattern.sub(' ', text)

    pattern = re.compile('(Mr|Mrs|etc|St|Esq)\.') # hack to stop sentence tokenization after abbreviations
    text = pattern.sub('\g<1>', text)

    doc = nlp(" ".join(text.split()))

    # Merge badly-split sentences
    # Idea: if sentence starts with lower case, then merge with previous
    # Use a stack to store all the spans, then pop & span.merge() them all
    last_start=-1
    spans_to_merge = []
    for sentence in doc.sents:
        this_start = sentence.start
        if sentence[0].text.islower() and last_start > 0:
            span=doc[last_start:sentence.end]
            this_start = span.start
            spans_to_merge.append(span)
        last_start = this_start
    for i in range(0,len(spans_to_merge)):
        span = spans_to_merge.pop()
        span.merge()

    #(re-)split to sentences, to add START_TOKEN/END_TOKEN
    doc_tokens = [token for sentence in doc.sents for token in sentence_boundaries(sentence)]

    # Merge multi-token entities to single tokens
    # PROBLEM! Messes with token indices (probably?) so merges wrong tokens...
    #for ent in doc.ents:
        # ent.root.tag_  = pos tag;
        # label_ = GPE (place) or PERSON, ORG, CARDINAL (number) or...
        # ent.merge(ent.root.tag_, ent.text, ent.label_)
    
    all_tokens = [token.text if is_plain_token(token) else "<" + type_lookup(token.ent_type_.upper()) + ">" for token in doc_tokens]
    entities = doc_to_types(doc)
    return {'tokens': all_tokens, 'entities': entities}


def test():
    filename = "/Users/dcorney/temp/106.txt"
    with open(filename, 'r') as myfile:
            text = myfile.read().replace('\n', ' ')
    # text = "A rap at this moment sounded on the door of the cosy apartment where Phileas Fogg was seated, and James Forster, \
    # the dismissed servant, man, person, etc. appeared at once.  \"The new servant,\" said he.  Their prominence was wholly gone  they were not even worth drowning\
    # so I removed that detail. It seemed a prompt good way of weeding out people that had got stalled, and a plenty good enough way for those others\
    # so I hunted up the two boys and said,  They went out back one night to stone the cat and fell down the well and got drowned."
    tokens = tokenize(text[0:50000])
    # #print(text[9000:11000])
    # print(tokens['tokens'])

if __name__ == '__main__':
    test()
