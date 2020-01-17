from Filesystems.Filesystem import Filesystem
import toml
import b2blaze


class B2FS(Filesystem):
    def __init__(self, bucket, username, password, *folder) -> None:
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
