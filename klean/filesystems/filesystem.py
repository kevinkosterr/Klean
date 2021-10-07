import yaml
from datetime import timedelta, datetime


class Filesystem:
    def __init__(self):
        """Base class for filesystems."""
        self.__files = self.list_files()
        self.__files_per_db = self.__get_files_per_db(self.__files)

    def __repr__(self):
        return "{}" % self.__class__

    @staticmethod
    def config(_config_cache=None):
        """
        Caches the configuration for speed optimization
        """
        if _config_cache is None:
            _config_cache = {}
        if _config_cache:
            return _config_cache
        with open("data/config.yaml") as c:
            c = yaml.load(c, Loader=yaml.Loader)
        _config_cache.update(c)
        return _config_cache

    @property
    def files(self):
        return self.__files

    @property
    def total_file_size(self):
        return self.__get_total_file_size()

    @property
    def kill_list_size(self):
        return self.__get_kill_list_file_size()

    def list_files(self):
        """Returns a reverse sorted list of files."""
        raise NotImplementedError()

    def calc_diff_between_dates(self, filedate1, filedate2):
        """
        Calculates the difference between two datetime objects
            :param filedate1: first datetime object
            :param filedate2: second datetime object to compare the first to
            :return: diff: the difference between the two datetime objects
        """
        diff = self.parse_filename_to_date(filedate1) - self.parse_filename_to_date(
            filedate2
        )
        return diff

    def parse_filename_to_date(self, filename):
        try:
            # splits the filename from the prefix to the datetime string
            prefix = self.config().get("main").get("prefix")
            file_to_parse = str(filename).split(prefix)[1].split(".")[0]
            # gets the datetime string and converts it to a datetime object
            file_date = datetime.strptime(
                str(file_to_parse).replace(";", "").replace("%3A", ":"),
                "%Y-%m-%d%" "H:%M:%S",
            )
            # if there is an error with parsing the datetime object out of the
            # filename, raise the error and show which filename can't be parsed
        except:
            print("error with", filename)
            raise
        return file_date

    def __get_files_per_db(self, files: list):
        files_per_db = {}
        prefix = self.config().get("main").get("prefix")
        # goes through the sorted files
        for filename in files:
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

    def __make_buckets(self, files_per_db: dict):
        for db_name in files_per_db.keys():
            # Creating an empty kill_list for every key in the dictionary
            # used for showing the amount of files per database that will be deleted.
            bucket1 = []
            bucket2 = []
            bucket3 = []
            bucket4 = []
            bucket5 = []
            # the first database filename for a database name
            first_element = files_per_db[db_name][0]
            for cursor in files_per_db[db_name]:
                diff = self.calc_diff_between_dates(first_element, cursor)
                # period in days is configurable.
                # if difference is smaller than or the same as period in days in config.toml
                # append it to the first bucket.
                if diff <= timedelta(
                    days=self.config().get("bucket_first").get("period_in_days")
                ):
                    bucket1.append(cursor)
                # If difference is smaller as the period in days append to the second bucket. etc
                elif diff <= timedelta(
                    days=self.config().get("bucket_second").get("period_in_days")
                ):
                    bucket2.append(cursor)
                elif diff <= timedelta(
                    days=self.config().get("bucket_third").get("period_in_days")
                ):
                    bucket3.append(cursor)
                elif diff <= timedelta(
                    days=self.config().get("bucket_fourth").get("period_in_days")
                ):
                    bucket4.append(cursor)
                elif diff >= timedelta(
                    days=self.config().get("bucket_fifth").get("period_in_days")
                ):
                    bucket5.append(cursor)

            yield [bucket1, bucket2, bucket3, bucket4, bucket5]

    def __bucket_kill_list(self, bucket_start: list, bucket_to_compare: list, hours):
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
                bucket_to_compare = bucket_to_compare[
                    bucket_to_compare.index(last) + 1 :
                ]
            else:
                bucket_start = bucket_to_compare.pop(0)

        return kill_list

    def create_kill_lists(self):
        kill_list = []
        b_conf = self.config().get("buckets")
        for buckets in self.__make_buckets(files_per_db=self.__files_per_db):
            # we're ignoring the first bucket completely as we always want the user to have recent backups to their
            # proposal.

            # we're extending the kill_list with items from the second bucket that should be deleted.
            kill_list.extend(
                self.__bucket_kill_list(
                    bucket_start=buckets[0][-1],
                    bucket_to_compare=buckets[1],
                    hours=b_conf[2].get("hours_between"),
                )
            )

            if buckets[1]:
                kill_list.extend(
                    self.__bucket_kill_list(
                        bucket_start=buckets[1][-1],
                        bucket_to_compare=buckets[2],
                        hours=b_conf[3].get("hours_between"),
                    )
                )

            if buckets[2]:
                kill_list.extend(
                    self.__bucket_kill_list(
                        bucket_start=buckets[2][-1],
                        bucket_to_compare=buckets[3],
                        hours=b_conf[4].get("hours_between"),
                    )
                )
            if buckets[3]:
                kill_list.extend(
                    self.__bucket_kill_list(
                        bucket_start=buckets[3][-1],
                        bucket_to_compare=[4],
                        hours=b_conf[5].get("hours_between"),
                    )
                )

        return kill_list

    def login(self):
        raise NotImplementedError()

    def __get_total_file_size(self):
        raise NotImplementedError()

    def __get_kill_list_file_size(self):
        raise NotImplementedError()
