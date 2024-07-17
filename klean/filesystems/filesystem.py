from datetime import datetime, timedelta
from collections import OrderedDict


class Filesystem:
    def __init__(self):
        self.sorted_files = self.get_sorted_files()
        self.files_per_db = self.get_files_per_db(self.sorted_files)

    def get_sorted_files(self):
        """
        Gets a sorted list of filenames.

            :return: sorted_files: a sorted list of filenames
        """
        raise NotImplementedError()

    def parse_filename_to_date(self, filename):
        """ Gets the datetime object from a filename

          :param filename: the filename of which you want the date to get parsed from
          :return: file_date: parsed datetime object out of the filename
        """
        try:
            prefix = self.config().get('main').get('prefix')
            # split on prefix and remove file extension from filename
            file_to_parse = str(filename).split(prefix)[1].split(".")[0]
            file_date = datetime.strptime(str(file_to_parse).replace(";", '').replace('%3A', ':'),
                                          "%Y-%m-%d%" "H:%M:%S")
        except Exception:
            print('error with', filename)
            raise
        return file_date

    def calc_diff_between_dates(self, filedate1, filedate2):
        """
        Calculates the difference between two datetime objects

            :param filedate1: first datetime object
            :param filedate2: second datetime object to compare the first to
            :return: diff: the difference between the two datetime objects
        """
        return self.parse_filename_to_date(filedate1) - self.parse_filename_to_date(filedate2)

    def get_files_per_db(self, sorted_files):
        """
        Gets the filenames per database and puts them into a dictionary

            :return: files_per_db: dictionary filled with filenames per database
        """
        files_per_db = {}
        prefix = self.config().get('main').get('prefix')
        # goes through the sorted files
        for filename in sorted_files:
            # if the given prefix isn't in the filename, continue
            if prefix not in filename:
                continue
            # key_name is the name of the database
            key_name = filename.split(prefix)[0]
            # if key doesn't exist yet, creates a key with an empty list
            if key_name not in files_per_db:
                files_per_db[key_name] = []
            # if key already exists, adds the filename as value
            files_per_db[key_name].append(filename)

        return files_per_db

    def create_kill_list(self, bucket_start: list, bucket_to_compare: list, hours):
        """
        Creates a kill_list based on the difference between each backup in the buckets

            :param bucket_start:
            :param bucket_to_compare:
            :param hours: the amount of hours there is allowed to be between each backup, this is configurable in
             config.toml
            :return: kill_list: a list of files to delete
        """
        kill_list = []
        while len(bucket_to_compare) > 1:
            for item in bucket_to_compare:
                # calculate the difference between each item in bucket_to_compare
                diff_start = self.calc_diff_between_dates(bucket_start, item)
                if diff_start < timedelta(hours=hours):
                    kill_list.append(item)
                else:
                    break
            # if there is nothing inside the kill_list
            # return an empty list
            if not kill_list:
                return []
            # last is the last item in the kill_list
            last = kill_list.pop()
            # if the last item is in the bucket you need to compare
            # then the last item won't be taken out of the kill_list
            if last in bucket_to_compare:
                bucket_start = last
                bucket_to_compare = bucket_to_compare[bucket_to_compare.index(last) + 1:]
            else:
                bucket_start = bucket_to_compare.pop(0)

        return kill_list

    def store_files_in_buckets(self, files_per_db):
        """
        Stores the filenames in buckets.

            :return: kill_list: list of files to delete
        """
        kill_list = []
        for db_name in files_per_db.keys():
            database_kill_list = []

            # We must keep the order as given by the config.toml, hence we need the OrderedDict here.
            # This is required mainly for keeping backwards compatibility.
            buckets = OrderedDict((x, []) for x in self.config().keys() if x.lower().startswith('bucket'))
            bucket_names = list(buckets.keys())
            last_bucket_name = bucket_names[-1]

            first_element = files_per_db[db_name][0]
            for cursor in files_per_db[db_name]:
                diff = self.calc_diff_between_dates(first_element, cursor)
                for bucket in bucket_names:
                    bucket_config = self.config().get(bucket)
                    if diff <= timedelta(days=bucket_config.get('period_in_days')):
                        buckets[bucket].append(cursor)
                        break
                    elif (
                            bucket == last_bucket_name and
                            diff >= timedelta(days=self.config().get(last_bucket_name).get('period_in_days'))
                    ):
                        buckets[bucket].append(cursor)
                        break

            for idx, (bucket_name, bucket_filenames) in enumerate(buckets.items()):
                try:
                    next_bucket_name = bucket_names[idx + 1]
                    database_kill_list.extend(
                        self.create_kill_list(
                            bucket_filenames[-1],
                            buckets[next_bucket_name],
                            self.config().get(next_bucket_name).get('hours_between')
                                              )
                    )
                except IndexError:
                    break

            kill_list.extend(database_kill_list)

            print(db_name, 'files found', len(files_per_db[db_name]), '# kill list:', len(database_kill_list))
        return kill_list

    def kill_list_size(self, kill_list):
        raise NotImplementedError()

    def total_file_size(self):
        raise NotImplementedError()

    def delete_files(self, kill_list):
        raise NotImplementedError()
