import Filesystems.Filesystem
import toml
import b2blaze


class B2FS(Filesystems.Filesystem.Filesystem):
    def __init__(self, bucket, key_id, app_id, *folder):
        self.b2 = b2blaze.B2(key_id, app_id)
        self.bucket = self.b2.buckets.get(bucket)
        self.sorted_files = str(self.get_sorted_files())
        self.files_per_db = self.get_files_per_db(self.sorted_files)
        self.folder = folder
        super().__init__()

    @staticmethod
    def config(_config_cache={}):
        if _config_cache:
            return _config_cache
        _config_cache.update(toml.load('config.toml'))
        return _config_cache

    def get_sorted_files(self):
        """ Gets a sorted list of files.

                   :return: a sorted b2bucket
                   """
        return self.bucket.files.all()

    def confirm_delete(self, kill_list):
        confirm = input("Are you sure you want to delete these files? (y/n) ")
        if confirm == 'y':
            self.delete_files(kill_list)
        if confirm == 'n':
            exit()
        else:
            self.confirm_delete(kill_list)

    def delete_files(self, kill_list):
        for filename in self.sorted_files:
            if filename in kill_list:
                try:
                    filename.delete()
                    print(filename, 'removed')
                except 400:
                    print('ERROR WITH', filename)
                    raise
        print('All files have been deleted successfully.')
        exit()
