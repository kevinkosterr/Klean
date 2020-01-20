import Filesystems.Filesystem
import toml
import b2blaze
from datetime import timedelta


class B2FS(Filesystems.Filesystem.Filesystem):
    def __init__(self, bucket, key_id, app_id, *folder):
        self.b2 = b2blaze.B2(key_id, app_id)
        self.bucket = self.b2.buckets.get(bucket)
        self.file_names = str(self.get_file_names())
        self.files_per_db = self.get_files_per_db(self.file_names)
        self.folder = folder
        super().__init__()

    @staticmethod
    def config(_config_cache={}):
        if _config_cache:
            return _config_cache
        _config_cache.update(toml.load('config.toml'))
        return _config_cache

    def get_file_names(self):
        files_with_objects = {}
        for obj in self.bucket.files.all():
            filename = obj.file_name
            if filename not in files_with_objects:
                files_with_objects[filename] = []
            files_with_objects[filename].append(obj)
        return files_with_objects
        # return sorted([_.file_name for _ in self.bucket.files.all()], reverse=True)

    def store_files_in_buckets(self, files_per_db):
        """ Stores the files in buckets.

        :return: kill_list: list of files to delete
        """
        files_per_db = self.get_files_per_db(self.get_file_names())
        kill_list = []
        # Searches for db_names in files_per_db.keys()
        for db_name in files_per_db.keys():
            # Creating an empty kill_list for every key in the dictionary
            # used for showing the amount of files per database that will be deleted.
            this_kill_list = []
            bucket1 = []
            bucket2 = []
            bucket3 = []
            bucket4 = []
            bucket5 = []
            first_element = files_per_db[db_name][0]
            for cursor in files_per_db[db_name]:
                diff = self.calc_diff_between_dates(first_element, cursor)
                # Period in days is configurable.
                # If difference is smaller than or the same as period in days in config.toml
                # append it to the first bucket.
                if diff <= timedelta(days=self.config().get('bucket_first').get('period_in_days')):
                    bucket1.append(cursor)
                # If difference is smaller as the period in days append to the second bucket.
                elif diff <= timedelta(days=self.config().get('bucket_second').get('period_in_days')):
                    bucket2.append(cursor)
                elif diff <= timedelta(days=self.config().get('bucket_third').get('period_in_days')):
                    bucket3.append(cursor)
                elif diff <= timedelta(days=self.config().get('bucket_fourth').get('period_in_days')):
                    bucket4.append(cursor)
                elif diff >= timedelta(days=self.config().get('bucket_fifth').get('period_in_days')):
                    bucket5.append(cursor)

            try:
                this_kill_list.extend(
                    self.create_kill_list(bucket1[-1], bucket2,
                                          self.config().get('bucket_second').get('hours_between')))
                this_kill_list.extend(
                    self.create_kill_list(bucket2[-1], bucket3, self.config().get('bucket_third').get('hours_between')))
                this_kill_list.extend(
                    self.create_kill_list(bucket3[-1], bucket4,
                                          self.config().get('bucket_fourth').get('hours_between')))
                this_kill_list.extend(
                    self.create_kill_list(bucket4[-1], bucket5, self.config().get('bucket_fifth').get('hours_between')))
                kill_list.extend(this_kill_list)
            except IndexError:
                continue

            print(db_name, 'files found', len(files_per_db[db_name]), '# kill list:', len(this_kill_list))
        return kill_list

    def confirm_delete(self, kill_list):
        confirm = input("Are you sure you want to delete these files? (y/n) ")
        if confirm == 'y':
            self.delete_files(kill_list)
        if confirm == 'n':
            exit()
        else:
            self.confirm_delete(kill_list)

    def delete_files(self, kill_list):
        for filename in self.file_names:
            if filename in kill_list:
                try:

                    print(filename, 'removed')
                except 400:
                    print('ERROR WITH', filename)
                    raise
        print('All files have been deleted successfully.')
        exit()
