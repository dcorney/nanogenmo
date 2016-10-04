import re

# this is a class, with members: tokens,
# methods: toString(), score, tokenize
# But should it just be a collection of static fns?


class Sentence(object):

    def __init__(self, tokens):
        self._tokens = tokens[1:-1]  # remove first & last tokens (end-markers)
        self.fix_sentence()
        self._score = self.evaluate_sentence()

        text = " ".join(self._tokens)
        b = {"''": '"', " ,": ",", ' .': '.', " 's": "'s", " n't": "n't"}
        for x, y in b.items():
            text = text.replace(x, y)

        self._text = text
        # return {"text": self._text, "score": score}

    def fix_sentence(self):
        """
        normalise quote-tokens etc.
        """
        # normalise double quotation (")
        p1 = re.compile("[\u201c\u201d\u201e\u201f\u275d\u275e\u2e0c]")
        p2 = re.compile("[\u2018\u2019\u201a\u201b\u275b\u275c\u2e0d\u0060]")
        for i, t in enumerate(self._tokens):
            self._tokens[i] = p2.sub("'", (p1.sub('"', t)))

    def evaluate_sentence(self):
        """
        Score sentence: too long? Odd count of quotes?
        Low score may lead to later rejection
        """
        self._score = 0
        length = len(self._tokens)
        self._score += (50 - length)
        counter = 0
        for t in self._tokens:
            if t.strip() == '"' or t.strip() == "''":
                counter += 1
        if counter % 2 == 1:
            self._score -= 50
        # print("Has " + str(counter) + " quotes; score " + str(self._score))
        return self._score

    def display(self):
        print(self._text + "  (" + str(self._score) + ")")

    def get_text(self):
        return(self._text)
