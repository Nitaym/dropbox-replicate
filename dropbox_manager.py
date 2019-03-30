import dropbox
import os
import datetime
import time
import utils
from multiprocessing.pool import ThreadPool

class DropboxManager:
    MAX_THREADS = 8

    def __init__(self, token):
        self.dbx = dropbox.Dropbox(token)

    def upload(self, fullname, folder, subfolder, name, overwrite=False):
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
            res = self.dbx.files_upload(data, path, mode, client_modified=datetime.datetime.now(), mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None
        print('uploaded as', res.name.encode('utf8'))
        return res

    def download(self, folder, subfolder, name):
        """Download a file.

        Return the bytes of the file, or None if it doesn't exist.
        """
        path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
        while '//' in path:
            path = path.replace('//', '/')

        try:
            md, res = self.dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None

        data = res.content
        # print(len(data), 'bytes; md:', md)
        return data

    def list_files(self, folder):
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
                res = self.dbx.files_list_folder(path)
            except dropbox.exceptions.ApiError as err:
                print('Folder listing failed for %s -- assumed empty: %s', (path, err))
                return dict()
            else:
                has_more = res.has_more
                for entry in res.entries:
                    rv[entry.name] = entry
        return rv

    def download_folder(self, dropbox_folder, local_folder):
        ls = self.list_files(dropbox_folder)

        if len(ls) == 0:
            return

        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        download_list = []

        # Scan files needed to be downloaded
        file_number = 0
        file_count = len(ls)
        for file in ls:
            local_filename = local_folder + '/' + file
            download = True

            message = '[%d of %d - %s] ' % (file_number, file_count, file)
            if os.path.isfile(local_filename):
                file_size = os.path.getsize(local_filename)
                needed_size = ls[file].size
                if file_size == needed_size:
                    message += 'File is identical on server and locally. Skipping. '
                    download = False
                else:
                    message += 'To be overwritten. '

            if download:
                download_list += [(dropbox_folder, local_filename, file_number)]
                message += 'To be downloaded.'
            print(message)
            file_number += 1

        total_download_count = len(download_list)
        download_list = [download + (index, total_download_count, ) for download, index in zip(download_list, range(total_download_count))]

        print("Starting %d downloads..." % total_download_count)
        results = ThreadPool(self.MAX_THREADS).imap_unordered(self.parallel_download, download_list)
        end_results = []
        for result in results:
            end_results += [result]

    def parallel_download(self, params):
        dropbox_folder, local_filename, file_number, total_files_count = params
        start = time.time()
        with open(local_filename, 'wb') as f:
            file = os.path.basename(local_filename)
            data = self.download(dropbox_folder, '', file)
            f.write(data)
            time_elapsed = time.time() - start
            speed = len(data) / time_elapsed
            speed, units = utils.good_units(speed)
            units += '/s'
            size, size_units = utils.good_units(len(data))
        message = '[%d of %d - %s] ' % (file_number, total_files_count, file)
        message = 'Downloaded. Size: %3.2f%s (%3.2f%s)' % (size, size_units, speed, units)
        print(message)
