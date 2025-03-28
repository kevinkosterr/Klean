import os

from klean.filesystems.filesystem import Filesystem
from typing import List

from klean.exceptions import KleanError


class LocalFS(Filesystem):
    def __init__(self, working_dir: str, configuration: dict) -> None:
        self.working_dir: str = working_dir
        super().__init__(configuration)

    @staticmethod
    def convert_to_mb(value: int) -> float:
        """Convert a given value (in bytes) to megabytes."""
        return round(float(value * 0.000001), 3)

    def get_sorted_files(self) -> List[str]:
        """
        Gets a sorted list of filenames
        :return: a sorted os.listdir
        """
        try:
            return sorted(os.listdir(self.working_dir), reverse=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"Can't find directory: '{self.working_dir}', please specify an existing directory "
                                    "in your configuration file")

    def kill_list_size(self, kill_list: List[str]) -> int:
        """
        Calculates the total size of the files that will be deleted.

        :param kill_list: the kill_list created in store_files_in_buckets()
        :return: kill_list_size: size of all files that will be deleted
        """
        return sum([os.path.getsize(os.path.join(self.working_dir, filename)) for filename in kill_list])

    def total_file_size(self) -> int:
        """
        Calculates the total file size of a directory.

        :return: total_size: total file size of the directory given in config.toml
        """
        return sum(os.path.getsize(f) for f in os.listdir(self.working_dir) if os.path.isfile(f))

    def delete_files(self, kill_list: List[str], verbose: bool = False) -> None:
        """
        Deletes the files based on the filenames in kill_list

        :param kill_list: the kill_list extended by store_files_in_buckets()
        :param verbose:
        """
        deleted_files = []
        for filename in os.listdir(self.working_dir):
            if filename in kill_list:
                try:
                    os.remove(os.path.join(self.working_dir, filename))
                    deleted_files.append(filename)
                    if verbose:
                        print(filename, 'removed')
                except OSError as e:
                    raise KleanError(f"Couldn't remove file '{filename}' with error: {str(e)}")
        print(f"{len(deleted_files)} files have been deleted successfully")
