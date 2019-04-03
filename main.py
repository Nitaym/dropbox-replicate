from dropbox_manager import DropboxManager
import bucket_manager
import os

def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
    token = lines[0]
    token = token.strip()
    return token

def download_folder(local_folder, remote_folder):
    token = read_token()
    dbx = DropboxManager(token)
    dbx.download_folder(remote_folder, local_folder)
    # dbx.list_files(remote_folder)

def upload_folder(local_folder, bucket_name, s3_folder_name):
    bucket = bucket_manager.BucketManager(bucket_name)
    bucket.upload_folder(local_folder, s3_folder_name)


def glacier_tests():
    glacier = boto3.client('glacier')
    # Print out bucket names
    l = glacier.list_vaults()
    for vault in l['VaultList']:
        print(vault)


def main():
    remote_folder = '/קלטות של סבא'
    local_folder = 'Tapes'
    bucket_name = 'saba-tapes'
    print("===============================================")
    print("Downloading from Dropbox...")
    download_folder(local_folder, remote_folder)
    print("")
    print("===============================================")
    print("Uploading to S3...")
    upload_folder(local_folder, bucket_name, 'Tapes')



if __name__ == "__main__":
    main()
