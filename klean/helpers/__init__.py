from klean.exceptions import KleanError
from klean.filesystems import Filesystem, LocalFS, B2FS

def get_file_system(file_system_string: str, configuration: dict) -> Filesystem:
    """
    Retrieve a filesystem object based on the given file system string.
    :param file_system_string:
    :param configuration:
    :return: a filesystem instance.
    """
    match file_system_string:
        case "local":
            directory: str = configuration.get('LocalFS').get('directory')
            return LocalFS(directory, configuration)
        case "b2":
            b2_configuration: dict = configuration.get('B2Blaze')
            bucket: str = b2_configuration.get('bucket')
            key_id: str = b2_configuration.get('key_id')
            app_key: str = b2_configuration.get('app_key')
            return B2FS(bucket, key_id, app_key, configuration)
        case _:
            raise KleanError(f"Unknown Filesystem: {file_system_string}")
