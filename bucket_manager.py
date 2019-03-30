import boto3
import botocore
import os
import time
import utils


class BucketManager:
    def __init__(self, bucket_name):
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(bucket_name)

    def get_file_list(self):
        ls = self.bucket.objects.all()
        ls = {item.key: item for item in ls}
        return ls

    def upload_file(self, local_filename, s3_filename):
        self.bucket.upload_file(local_filename, s3_filename)

    def upload_folder(self, local_folder):
        remote_files = self.get_file_list()
        file_number = 0
        files_to_upload = os.listdir(local_folder)
        file_count = len(files_to_upload)

        for file in files_to_upload:
            local_filename = local_folder + '/' + file
            upload = True
            file_size = os.path.getsize(local_filename)

            message = '[%d of %d - %s] ' % (file_number, file_count, file)
            if file in remote_files:
                remote_size = remote_files[file].size
                if file_size == remote_size:
                    message += 'File is identical on server and locally. Skipping. '
                    upload = False
                else:
                    message += 'Overwriting file. '

            if upload:
                start = time.time()
                with open(local_filename, 'wb') as f:
                    self.upload_file(local_filename, file)
                    time_elapsed = time.time() - start
                    speed = file_size / time_elapsed
                    speed, units = utils.good_units(speed)
                    units += '/s'
                    size, size_units = utils.good_units(file_size)
                message += 'Uploaded. Size: %3.2f%s (%3.2f%s)' % (size, size_units, speed, units)

            print(message)
            file_number += 1


if __name__ == "__main__":
    bucket = BucketManager('saba-tapes')
    ls = bucket.get_file_list_iterator()
    ls = {item.key:item for item in ls}
    print(ls)
