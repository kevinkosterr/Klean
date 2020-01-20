import Filesystems.Filesystem
import toml
import os
from datetime import timedelta


class LocalFS(Filesystems.Filesystem.Filesystem):
    def __init__(self, working_dir):
        self.working_dir = working_dir
        super().__init__()

    @staticmethod
    def config(_config_cache={}):
        if _config_cache:
            return _config_cache
        _config_cache.update(toml.load('config.toml'))
        return _config_cache

    def get_file_names(self):
        """ Gets a sorted list of files.

            :return: a sorted os.listdir
            """
        # sorted_files = sorted(os.listdir(config().get('main').get('directory')), reverse=True)
        # return a reverse sorted file list
        return sorted(os.listdir(self.working_dir), reverse=True)

    def kill_list_size(self, kill_list):
        """ Calculates the total size of the files that will be deleted.

        :param kill_list: the kill_list created in store_files_in_buckets()
        :return: kill_list_size: size of all files that will be deleted
        """
        kill_list_size = 0
        for filename in kill_list:
            file_size = os.path.getsize(f"{self.working_dir}\\{filename}")
            kill_list_size += file_size
        return kill_list_size

    def total_file_size(self):
        """ Calculates the total file size of a directory.

            :return: total_size: total file size of the directory given in config.toml
            """
        total_size = sum(
            os.path.getsize(f) for f in os.listdir(self.working_dir) if os.path.isfile(f))
        return total_size

    def confirm_delete(self, kill_list):
        """ Asks the user for confirmation whether the files should be deleted or not.

            :param kill_list: the kill_list created in store_files_in_buckets()
            """
        delete_file_size = round(float(self.kill_list_size(kill_list) * 0.000001), 3)
        total_size = round(float(self.total_file_size() * 0.000001), 3)
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
        file_dir = self.working_dir
        for filename in os.listdir(file_dir):
            if filename in kill_list:
                try:
                    os.remove(os.path.join(file_dir, filename))
                    print(filename, 'removed')
                except OSError:
                    print(f'ERROR with {filename}')
                    raise
        print(f'files have been deleted succesfully')
        exit()
