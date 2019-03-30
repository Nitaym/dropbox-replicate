from dropbox_manager import DropboxManager
import boto_manager
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

def upload_folder(local_folder, bucket_name):
    boto = boto_manager.BotoManager()
    for file in os.listdir(local_folder):
        boto.upload_file(bucket_name, local_folder + '/' + file, file)
        print('Uploaded %s' % file)


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
    download_folder(local_folder, remote_folder)
    upload_folder(local_folder, bucket_name)



if __name__ == "__main__":
    main()
