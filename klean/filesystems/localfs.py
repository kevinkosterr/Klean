from .filesystem import Filesystem
import toml
import os


class LocalFS(Filesystem):
    def __init__(self, working_dir):
        self.working_dir = working_dir
        super().__init__()

    @staticmethod
    def config(_config_cache={}):
        """
        Caches the configuration for speed optimization
        """
        if _config_cache:
            return _config_cache
        _config_cache.update(toml.load('data/config.toml'))
        return _config_cache

    @staticmethod
    def convert_to_mb(value):
        """Convert a given value (in bytes) to megabytes."""
        return round(float(value * 0.000001), 3)

    def get_sorted_files(self):
        """
        Gets a sorted list of filenames

            :return: a sorted os.listdir
        """
        return sorted(os.listdir(self.working_dir), reverse=True)

    def kill_list_size(self, kill_list):
        """
        Calculates the total size of the files that will be deleted.

            :param kill_list: the kill_list created in store_files_in_buckets()
            :return: kill_list_size: size of all files that will be deleted
        """
        return sum([os.path.getsize(os.path.join(self.working_dir, filename)) for filename in kill_list])

    def total_file_size(self):
        """
        Calculates the total file size of a directory.

            :return: total_size: total file size of the directory given in config.toml
        """
        return sum(os.path.getsize(f) for f in os.listdir(self.working_dir) if os.path.isfile(f))

    def confirm_delete(self, kill_list):
        """
        Asks the user for confirmation whether the files should be deleted or not.

        :param kill_list: the kill_list created in store_files_in_buckets()
        """
        delete_file_size = self.convert_to_mb(self.kill_list_size(kill_list))
        total_size = self.convert_to_mb(self.total_file_size())

        print(f'\ntotal file size of files in directory: {total_size} MB')
        print(f'# kill list file size: {delete_file_size} MB')

        confirm = input("\nAre you sure you want to delete these files? (y/n) ")
        if confirm == 'y':
            self.delete_files(kill_list)
        elif confirm == 'n':
            exit()
        else:
            self.confirm_delete(kill_list)

    def delete_files(self, kill_list):
        """
        Deletes the files based on the filenames in kill_list

            :param kill_list: the kill_list extended by store_files_in_buckets()
        """
        file_dir = self.working_dir
        for filename in os.listdir(file_dir):
            # if the filename is in the kill_list delete it
            if filename in kill_list:
                try:
                    os.remove(os.path.join(file_dir, filename))
                    print(filename, 'removed')
                # prints ERROR follow by the filename if an OSError occurs
                except OSError:
                    print(f'ERROR with {filename}')
                    raise
        print(f'files have been deleted succesfully')
