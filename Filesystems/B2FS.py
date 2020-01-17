import Filesystems.Filesystem
import toml
import b2blaze


class B2FS(Filesystems.Filesystem.Filesystem):
    def __init__(self, bucket, username, password, *folder):
        self.b2 = b2blaze.B2(username, password)
        self.bucket = self.b2.buckets.get(bucket)
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
        return sorted(self.bucket.files.all())
