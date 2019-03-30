import boto3
import botocore
import os
import time
import utils
from multiprocessing.pool import ThreadPool


class BucketManager:
    MAX_THREADS = 8

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

        upload_list = []
        for file in files_to_upload:
            local_filename = local_folder + '/' + file
            upload = True
            file_size = os.path.getsize(local_filename)

            message = '[%d of %d - %s] ' % (file_number + 1, file_count, file)
            if file in remote_files:
                remote_size = remote_files[file].size
                if file_size == remote_size:
                    message += 'File is identical on server and locally. Skipping. '
                    upload = False
                else:
                    message += 'To be overwritten. '

            if upload:
                upload_list += [(local_filename, )]
            print(message)
            file_number += 1

        total_upload_count = len(upload_list)
        upload_list = [upload + (index, total_upload_count, ) for upload, index in zip(upload_list, range(total_upload_count))]

        print("Starting %d uploads..." % total_upload_count)
        results = ThreadPool(self.MAX_THREADS).imap_unordered(self.parallel_upload, upload_list)
        end_results = []
        for result in results:
            end_results += [result]


    def parallel_upload(self, params):
        local_filename, file_number, total_upload_count = params
        file_size = os.path.getsize(local_filename)
        file = os.path.basename(local_filename)
        start = time.time()
        self.upload_file(local_filename, file)
        time_elapsed = time.time() - start
        time_elapsed = time_elapsed if time_elapsed > 0 else 1
        speed = file_size / time_elapsed
        speed, units = utils.good_units(speed)
        units += '/s'
        size, size_units = utils.good_units(file_size)
        message = '[%d of %d - %s] ' % (file_number + 1, total_upload_count, file)
        message += 'Uploaded. Size: %3.2f%s (%3.2f%s)' % (size, size_units, speed, units)
        print(message)


if __name__ == "__main__":
    bucket = BucketManager('saba-tapes')
    ls = bucket.get_file_list()
    print(ls)
