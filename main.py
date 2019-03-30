# import boto3
import dropbox
import os
import datetime



def upload(dbx, fullname, folder, subfolder, name, overwrite=False):
    """Upload a file.

    Return the request response, or None in case of error.
    """
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)
    with open(fullname, 'rb') as f:
        data = f.read()

    try:
        res = dbx.files_upload(data, path, mode, client_modified=datetime.datetime.now(), mute=True)
    except dropbox.exceptions.ApiError as err:
        print('*** API error', err)
        return None
    print('uploaded as', res.name.encode('utf8'))
    return res

def download(dbx, folder, subfolder, name):
    """Download a file.

    Return the bytes of the file, or None if it doesn't exist.
    """
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')

    try:
        md, res = dbx.files_download(path)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None

    data = res.content
    # print(len(data), 'bytes; md:', md)
    return data

def list_files(dbx, folder):
    """List a folder.

    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = folder
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')

    rv = {}
    has_more = True
    while has_more:
        try:
            res = dbx.files_list_folder(path)
        except dropbox.exceptions.ApiError as err:
            print('Folder listing failed for %s -- assumed empty: %s', (path, err))
            return dict()
        else:
            has_more = res.has_more
            for entry in res.entries:
                rv[entry.name] = entry
    return rv


def download_folder(dbx, dropbox_folder, local_folder):
    ls = list_files(dbx, dropbox_folder)

    if len(ls) == 0:
        return

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    for file in ls:
        with open(local_folder + '/' + file, 'wb') as f:
            f.write(download(dbx, dropbox_folder, '', file))
        print('Downloaded %s' % file)


def read_token():
    with open('token.txt', 'r') as f:
        lines = f.readlines()
    token = lines[0]
    token = token.strip()
    return token

def download_dropbox():
    token = read_token()
    dbx = dropbox.Dropbox(token)
    folder_name = '/קלטות של סבא'
    download_folder(dbx, folder_name, 'F:/test')


def glacier_tests():
    glacier = boto3.client('glacier')
    # Print out bucket names
    l = glacier.list_vaults()
    for vault in l['VaultList']:
        print(vault)

def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))


def main():
    download_dropbox()


if __name__ == "__main__":
    main()
