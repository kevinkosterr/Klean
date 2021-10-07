from klean.filesystems.localfs import LocalFS
from klean.filesystems.b2fs import B2FS


class BackupCleaner:
    def __init__(self, filesystem):
        self.filesystem = self._determine_filesystem(filesystem)

    def _determine_filesystem(self, fs: str):
        match fs:
            case "local":
                return LocalFS()
            case "b2":
                return B2FS()
