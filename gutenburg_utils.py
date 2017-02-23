import sys
sys.path.append("../Gutenberg")
from gutenberg.cleanup import strip_headers
from gutenberg.acquire import load_etext
import string
import time
import boto3
# NB: Full install of gutenburg requries BSD-DB which I don't want/need
# So just add the source files to the sys.path and import...

session = boto3.Session(profile_name='personal')
s3_client = session.client('s3')


def to_s3(filename, keyname):
    print("Writing " + filename + " to " + keyname)
    bucket = 'clean-guten'
    s3_client.upload_file(filename, bucket, keyname)


def get_clean_dump(fileid):
    try:
        text = strip_headers(load_etext(fileid)).strip()
        raw_title = text.split('\n', 1)[0]
        tidy_title = raw_title.translate(str.maketrans('', '', string.punctuation))
        title = str(fileid) + "_" + tidy_title + ".txt"
        print("title: " + title)
        filename = "/Users/dcorney/Documents/books/clean-guten/" + title
        dump_file = open(filename, "w")
        dump_file.write(text.encode('ascii', 'ignore').decode('ascii'))
        dump_file.close()
        to_s3(filename, title.replace(" ", "_"))
        time.sleep(10)
    except Exception:
        pass


def from_s3(key_number, filename):
    bucket_name = "clean-guten"
    for key in s3_client.list_objects(Bucket=bucket_name, Prefix=key_number + "_")['Contents']:
        print("Downloading " + key['Key'])
        s3_client.download_file(bucket_name, key['Key'], filename)


#[get_clean_dump(f) for f in range(400, 401)]

# fileid = 300
# get_clean_dump(fileid)


# Upload to S3 alread-downloaded files: (one-off)
#  work_dir = "/Users/dcorney/Documents/books/clean-guten/"
# [to_s3(work_dir + fn, fn.replace(" ","_")) for fn in os.listdir(work_dir) if fn.endswith(".txt") ]
