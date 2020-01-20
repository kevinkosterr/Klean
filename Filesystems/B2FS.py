import Filesystems.Filesystem
import toml
import b2blaze


class B2FS(Filesystems.Filesystem.Filesystem):
    def __init__(self, bucket, key_id, app_id, *folder):
        self.b2 = b2blaze.B2(key_id, app_id)
        self.bucket = self.b2.buckets.get(bucket)
        self.sorted_files = self.get_sorted_files()
        self.files_per_db = self.get_files_per_db(self.sorted_files)
        self.folder = folder
        self.filenames_to_obj_map = {}
        super().__init__()

    @staticmethod
    def config(_config_cache={}):
        if _config_cache:
            return _config_cache
        _config_cache.update(toml.load('config.toml'))
        return _config_cache

    def get_sorted_files(self):
        # putting the filenames as keys into a dictionary
        # every value of a filename is a B2File object
        self.filenames_to_obj_map = {_.file_name: _ for _ in self.bucket.files.all()}
        filenames = self.filenames_to_obj_map.keys()
        return sorted(filenames, reverse=True)

    def confirm_delete(self, kill_list):
        confirm = input("Are you sure you want to delete these files? (y/n) ")
        if confirm == 'y':
            self.delete_files(kill_list)
        if confirm == 'n':
            exit()

    def delete_files(self, kill_list):
        for filename in kill_list:
            obj = self.filenames_to_obj_map[filename]
            path = b2blaze.API.delete_file_version
            params = {
                'fileId': obj.file_id,
                'fileName': obj.file_name
            }
            response = obj.connector.make_request(path=path, method='post', params=params)
            if not response.status_code == 200:
                raise FileNotFoundError('Error during file deletion of {}:{}'.format(filename, response.value))
            obj.deleted = True
            print(filename, 'deleted')
        print('All files have been deleted successfully.')
