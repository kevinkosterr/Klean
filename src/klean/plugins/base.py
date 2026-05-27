import typer

from pathlib import Path
from urllib.parse import unquote
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import timedelta, datetime
from collections import defaultdict, OrderedDict


class FileSystemPlugin(ABC):
    name: str
    help: str

    def __init__(self, config: dict):
        self.config = config
        self.sorted_filenames = self.get_sorted_filenames()
        self.filenames_per_database = self.get_filenames_per_database(
            self.sorted_filenames
        )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name") or cls.name is None:
            raise TypeError(f"{cls.__name__} must define class attribute 'name'")

    @abstractmethod
    def get_sorted_filenames(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def delete_files(self, to_delete: List[str], verbose: Optional[bool] = False):
        raise NotImplementedError()

    @staticmethod
    def replace_multiple(value: str, to_replace: list[str]) -> str:
        """
        Replace multiple values in a string with an empty string.

        :param value: value to replace other values in.
        :param to_replace: list of values to replace.
        """
        for item in to_replace:
            value = value.replace(item, "")
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

    def get_buckets(self) -> OrderedDict[str, List[str]]:
        """
        Retrieve a mapping of bucket names to empty lists.

        This method generates an ordered dictionary where the keys are
        bucket-like names extracted from `self.config` that begin with the
        string "bucket" (case-insensitive). The values for all keys are
        empty lists.

        :return: An ordered dictionary containing bucket names as keys and
                 empty lists as values.
        :rtype: OrderedDict[str, List[str]]
        """
        return OrderedDict(
            (x, []) for x in self.config.keys() if x.lower().startswith("bucket")
        )

    def get_filenames_per_database(
        self, sorted_filenames: List[str]
    ) -> Dict[str, List[str]]:
        """
        Get a list of filenames per database. Returns a dictionary where the keys are database names
        and the values are lists of filenames.
        :param sorted_filenames: All filenames sorted alphabetically.
        :return: Dictionary with database names as keys and lists of filenames as values.
        """
        files_per_database = defaultdict(list)
        prefix = self.config.get("main").get("prefix", None)

        for filename in sorted_filenames:
            # No prefix exists, meaning the folder likely has no separation between databases in the target location.
            if not prefix:
                files_per_database["default"].append(filename)
                continue

            # Ignore this file, as it probably does not belong here anyway.
            if prefix not in filename:
                continue

            database_name: str = filename.split(prefix)[0]
            files_per_database[database_name].append(filename)

        return dict(files_per_database)

    def parse_date_from_filename(self, filename: str) -> datetime:
        """
        Gets the datetime object from a filename

        :param filename: the filename of which you want the date to get parsed from
        :return: file_date: parsed datetime object out of the filename
        """
        main_configuration = self.config.get("main")
        suffix = main_configuration.get("suffix")
        prefix = main_configuration.get("prefix")
        try:
            date_string_to_parse = self.filename_to_date_string(
                filename, prefix, suffix
            )

            if to_replace := main_configuration.get("replace_extra"):
                date_string_to_parse = self.replace_multiple(
                    date_string_to_parse, to_replace
                )

            date_format = main_configuration.get(
                "date_format"
            ) or main_configuration.get("datetime_format")

            return datetime.strptime(date_string_to_parse, date_format)
        except Exception as e:
            raise ValueError(
                f"Error while parsing filename string to date, with {filename}. Got error: {str(e)}"
            )

    def calculate_difference_between_file_dates(
        self, filename_a: str, filename_b: str
    ) -> timedelta:
        return self.parse_date_from_filename(
            filename_a
        ) - self.parse_date_from_filename(filename_b)

    def __create_bucket_kill_list(
        self, bucket_start: str, bucket_to_compare: List[str], hours_between: int
    ) -> List[str]:
        kill_list: List[str] = []

        while len(bucket_to_compare) > 1:
            for item in bucket_to_compare:
                # calculate the difference between each item in bucket_to_compare
                diff_start = self.calculate_difference_between_file_dates(bucket_start, item)
                if diff_start < timedelta(hours=hours_between):
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

    def create_kill_list(self, filenames_per_database: Dict[str, List[str]]) -> List[str]:
        """
        Create a list of all filenames to be deleted.
        :return: List of filenames to be deleted.
        """
        kill_list: List[str] = []
        all_buckets = self.get_buckets()
        bucket_names = list(all_buckets.keys())
        last_bucket_name: str = bucket_names[-1]

        for database_name in filenames_per_database.keys():
            database_buckets = all_buckets.copy()
            database_kill_list: List[str] = []
            database_filenames = filenames_per_database[database_name]

            first_filename = database_filenames[0]
            for cursor in database_filenames:
                diff: timedelta = self.calculate_difference_between_file_dates()
                for bucket_name in bucket_names:
                    bucket_config = self.config.get(bucket_name)
                    # Determine if this file belongs inside the current bucket.
                    if diff <= timedelta(days=bucket_config.get("period_in_days")):
                        database_buckets[bucket_name].append(cursor)
                        break
                    # Otherwise, if this is the last bucket and the file is too old, remove it.
                    elif bucket_name == last_bucket_name and diff >= timedelta(
                        days=self.config.get(last_bucket_name).get("period_in_days")
                    ):
                        database_buckets[bucket_name].append(cursor)
                        break

            for index, (bucket_name, bucket_filenames) in enumerate(database_buckets.items()):
                try:
                    next_bucket_name: str = bucket_names[index + 1]
                    database_kill_list.extend(
                        self.__create_bucket_kill_list(
                            bucket_filenames[-1],
                            database_buckets[next_bucket_name],
                            self.config.get(next_bucket_name).get("hours_between")
                        )
                    )
                except IndexError:
                    break

            kill_list.extend(database_kill_list)
            typer.echo(f"Found {len(database_filenames)} files in database {database_name}, {len(database_kill_list)} files will be deleted.")

        return kill_list

