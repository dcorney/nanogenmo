import boto3

session = boto3.Session(profile_name='personal')
s3_client = session.client('s3')


def to_s3(filename, keyname, bucket='clean-guten'):
    print("Writing " + filename + " to " + keyname)
    s3_client.upload_file(filename, bucket, keyname)


def from_s3(key_number, filename, bucket='clean-guten'):
    for key in s3_client.list_objects(Bucket=bucket,
                                      Prefix=key_number + "_")['Contents']:
        print("Downloading " + key['Key'])
        s3_client.download_file(bucket, key['Key'], filename)
