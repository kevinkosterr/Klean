from klean import filesystems
import yaml


class KleanError(RuntimeError):
    pass


class BackupCleaner:
    def __init__(self, fs_name):
        self.__fs = self.__determine_filesystem(fs_name)

    @property
    def filesystem(self):
        return self.__fs

    @staticmethod
    def config(_config_cache=None):
        """
        Caches the configuration for speed optimization
        """
        if _config_cache is None:
            _config_cache = {}
        if _config_cache:
            return _config_cache
        with open('data/config.yaml') as c:
            c = yaml.load(c, Loader=yaml.Loader)
        _config_cache.update(c)
        return _config_cache

    @staticmethod
    def __determine_filesystem(fs_name: str):
        match fs_name:
            case "local":
                return filesystems.LocalFS()
            case "b2":
                return filesystems.B2FS()
            case _:
                raise KleanError("Unsupported filesystem.")

    def login(self):
        return self.__fs.login()
