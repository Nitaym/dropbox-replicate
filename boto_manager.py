import boto3
import botocore


class BotoManager:
    def __init__(self):
        pass

    def upload_file(self, bucket_name, local_filename, s3_filename):
        s3 = boto3.resource('s3')
        s3.Bucket(bucket_name).upload_file(local_filename, s3_filename)