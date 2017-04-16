import tokenizers
import sys
sys.path.append("/Users/dcorney/github/dc/Gutenberg")
import gutenburg_utils as guten
import text_loader


def test():
    filename = "/tmp/103.txt"
    # guten.from_s3('103', filename)
    with open(filename, 'r', errors='ignore') as myfile:
               in_text = myfile.read().replace('\n', ' ')

    processed = tokenizers.tokenize(in_text[4000:4800])
    print(" ".join(processed['tokens'][0:200]))
    print(processed['entities'])


if __name__ == '__main__':
    test()
