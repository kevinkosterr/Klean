import toml
import os

from urllib.parse import unquote
from pathlib import Path
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import List, Dict

from klean.exceptions import KleanError


class Filesystem:
    def __init__(self, configuration: dict) -> None:
        self.config: dict = configuration
        self.sorted_files: List[str] = self.get_sorted_files()
        self.files_per_db: Dict[str, List[str]] = self.get_files_per_db(self.sorted_files)

    def get_sorted_files(self) -> List[str]:
        """
        Gets a sorted list of filenames.

        :return: sorted_files: a sorted list of filenames
        """
        raise NotImplementedError()

    @staticmethod
    def replace_multiple(value: str, to_replace: list[str]) -> str:
        """
        Replace multiple values in a string with an empty string.

        :param value: value to replace other values in.
        :param to_replace: list of values to replace.
        """
        for item in to_replace:
            value = value.replace(item, '')
        return value

    @staticmethod
    def filename_to_date_string(filename: str, prefix: str, suffix: str) -> str:
        """
        Strip a filename from everything excepts its date string.

        :param filename: full name of the file,
        :param prefix: prefix used to separate the file/database name from the date string
        :param suffix: suffix used to separate the file/database name from the date string
        """
        # if no prefix or suffix is supplied, its assumed that the user will not be needing a prefix/suffix to be able
        # to perform the parsing to a date.
        return unquote(Path(filename).stem.split(prefix)[1].split(suffix)[0])

    def parse_filename_to_date(self, filename: str) -> datetime:
        """
        Gets the datetime object from a filename

        :param filename: the filename of which you want the date to get parsed from
        :return: file_date: parsed datetime object out of the filename
        """
        main_configuration = self.config.get('main')
        suffix = main_configuration.get('suffix')
        prefix = main_configuration.get('prefix')
        try:
            date_string_to_parse = self.filename_to_date_string(filename, prefix, suffix)

            if to_replace := main_configuration.get('replace_extra'):
                date_string_to_parse = self.replace_multiple(date_string_to_parse, to_replace)

            date_format = main_configuration.get('date_format') or main_configuration.get('datetime_format')

            return datetime.strptime(date_string_to_parse, date_format)
        except Exception as e:
            raise KleanError(f"Error while parsing filename string to date, with {filename}. Got error: {str(e)}")

    def calc_diff_between_dates(self, filedate1, filedate2):
        """
        Calculates the difference between two datetime objects

            :param filedate1: first datetime object
            :param filedate2: second datetime object to compare the first to
            :return: diff: the difference between the two datetime objects
        """
        return self.parse_filename_to_date(filedate1) - self.parse_filename_to_date(filedate2)

    def get_files_per_db(self, sorted_files: List[str]) -> Dict[str, List[str]]:
        """
        Gets the filenames per database and puts them into a dictionary

            :return: files_per_db: dictionary filled with filenames per database
        """
        files_per_db: Dict[str, List[str]] = {}
        prefix = self.config.get('main').get('prefix')

        for filename in sorted_files:
            # ignore all files that don't have the prefix in them
            if prefix not in filename:
                continue

            database_name: str = filename.split(prefix)[0]
            if database_name not in files_per_db:
                files_per_db[database_name] = []
            files_per_db[database_name].append(filename)

        return files_per_db

    def create_kill_list(self, bucket_start: list, bucket_to_compare: list, hours) -> List[str]:
        """
        Creates a kill_list based on the difference between each backup in the buckets

            :param bucket_start:
            :param bucket_to_compare:
            :param hours: the amount of hours there is allowed to be between each backup, this is configurable in
             config.toml
            :return: kill_list: a list of files to delete
        """
        kill_list: List[str] = []
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

    def store_files_in_buckets(self, files_per_db: Dict[str, List[str]]) -> List[str]:
        """
        Stores the filenames in buckets.

            :return: kill_list: list of files to delete
        """
        kill_list: List[str] = []
        for db_name in files_per_db.keys():
            database_kill_list: List[str] = []

            # We must keep the order as given by the config.toml, hence we need the OrderedDict here.
            # This is required mainly for keeping backwards compatibility.
            buckets: OrderedDict = OrderedDict((x, []) for x in self.config.keys() if x.lower().startswith('bucket'))
            bucket_names: List[str] = list(buckets.keys())
            last_bucket_name: str = bucket_names[-1]

            first_element: str = files_per_db[db_name][0]
            for cursor in files_per_db[db_name]:
                diff: timedelta = self.calc_diff_between_dates(first_element, cursor)
                for bucket in bucket_names:
                    bucket_config: dict = self.config.get(bucket)
                    # Determine if this file belongs inside the current bucket.
                    if diff <= timedelta(days=bucket_config.get('period_in_days')):
                        buckets[bucket].append(cursor)
                        break
                    elif (
                            bucket == last_bucket_name and
                            diff >= timedelta(days=self.config.get(last_bucket_name).get('period_in_days'))
                    ):
                        buckets[bucket].append(cursor)
                        break

            for idx, (bucket_name, bucket_filenames) in enumerate(buckets.items()):
                try:
                    next_bucket_name: str = bucket_names[idx + 1]
                    database_kill_list.extend(
                        self.create_kill_list(
                            bucket_filenames[-1],
                            buckets[next_bucket_name],
                            self.config.get(next_bucket_name).get('hours_between')
                        )
                    )
                except IndexError:
                    break

            kill_list.extend(database_kill_list)

            print(db_name, 'files found', len(files_per_db[db_name]), '# kill list:', len(database_kill_list))
        return kill_list

    def kill_list_size(self, kill_list: List[str]) -> int:
        raise NotImplementedError()

    def total_file_size(self) -> int:
        raise NotImplementedError()

    def delete_files(self, kill_list: List[str], verbose: bool = False) -> None:
        raise NotImplementedError()
