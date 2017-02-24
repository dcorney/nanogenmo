#import nltk
from nltk import word_tokenize, sent_tokenize
from nltk.tag import StanfordNERTagger
from util import START_TOKEN, END_TOKEN

# TODO: use NER to replace PEOPLE, LOCATION, ORGANISATION tags with special tokens
# Then replace those with suitable tokens from another list
# Change tokenize() to return list of tokens + lists of instances of each type
# E.g. {tokens: ["PERSON" "said" to "PERSON" "'" "Hello" "there" "PERSON"] ,
#       people: ["John" "Mary" "Mary"], locations: [], organisations :[]}

st = StanfordNERTagger("resources/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz",
                       "resources/stanford-ner-2014-06-16/stanford-ner-3.4.jar")


def ner_tags(tokens):
    ner_tags = st.tag(tokens)
    tagged_tokens = [token if ner_type == 'O' else "<" +
                     ner_type + ">" for [token, ner_type] in ner_tags]
    trimmed_tokens = []
    for idx, tag in enumerate(tagged_tokens):
        if idx == 0 or tag != tagged_tokens[idx - 1]:
            trimmed_tokens.append(tag)
    return trimmed_tokens


def process_ner_tags(ner_tags):
    "Merge adjacent tags of the same type \
    (e.g. 'south' + 'africa' -> 'south africa')"
    merged_tags = []
    merged_token = ["", ""]
    for idx, (token, ner_type) in enumerate(ner_tags):
        if idx == 0:
            merged_token = [token, ner_type]
        else:
            if ner_type == "O":
                merged_tags.append(merged_token)
                merged_token = [token, ner_type]
            else:
                if ner_type == ner_tags[idx - 1][1]:
                    merged_token[0] += " " + token
                    merged_token[1] = ner_type
                else:
                    merged_tags.append(merged_token)
                    merged_token = [token, ner_type]
    merged_tags.append(merged_token)
    return(merged_tags)


def tokens_to_types(merged_tags):
    examples = {"ORGANIZATION": [], "PERSON": [], "LOCATION": []}
    tokens = []
    for [token, ner_type] in merged_tags:
        if ner_type == "O":
            tokens.append(token)
        else:
            examples[ner_type].append(token)
            tokens.append("<" + ner_type + ">")
    return {'tokens': tokens, 'entities': examples}


def tokenize_sentence(s):
    tk_list = word_tokenize(s)
    ner_tags = st.tag(tk_list)
    merged_tags = process_ner_tags(ner_tags)
    tokens_entities = tokens_to_types(merged_tags)
    tokens_entities['tokens'].insert(0, START_TOKEN)
    tokens_entities['tokens'].append(END_TOKEN)
    return tokens_entities

# TODO: move string labels into vars (org="ORGANIZATION" etc)
def tokenize(text):
    """
    Split text into sentences; then split sentences into tokens.
    Also tags entities and returns list of surface forms.
    """
    sents = sent_tokenize(text)
    flattened_tokens = []
    count = 0
    merged_entities = {"ORGANIZATION": [], "PERSON": [], "LOCATION": []}
    for s in sents:
        # all_tokens.append(tokenize_sentence(s))
        tokens_entities = tokenize_sentence(s)
        if count > 10:  # Skip first few sentences - may be contents page? Bit messy...
            tokens = tokens_entities['tokens']
            entities = tokens_entities['entities']
            flattened_tokens += (tokens)
            merged_entities['ORGANIZATION'] += entities['ORGANIZATION']
            merged_entities['PERSON'] += entities['PERSON']
            merged_entities['LOCATION'] += entities['LOCATION']
        count += 1
        if count % 25 == 0:
            print('Progress: {} / {}'.format(count, len(sents)))
            print(s)
            print(tokens)
            print(entities)
        if count > 1000:
            break
    return {'tokens': flattened_tokens, 'entities': merged_entities}
