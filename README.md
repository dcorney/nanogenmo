Write this! (Or generate it...)

Start Redis thus:
/usr/local/bin/redis-server ~/github/python/nanogenmo16/redis_ng16.conf

Then
python main.py
jekyll build
AWS_PROFILE=personal aws s3 sync /Users/dcorney/github/dc/dcorney.aws/_site s3://dcorney.com --region eu-west-1
