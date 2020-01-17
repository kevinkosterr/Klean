from datetime import datetime, timedelta


class Filesystem:
    def __init__(self):
        self.sorted_files = self.get_sorted_files()
        self.files_per_db = self.get_files_per_db(self.sorted_files)

    def get_sorted_files(self):
        raise NotImplementedError()

    def get_file_date(self, filename):
        """ Gets the datetime object from a filename

          :param filename: the filename of which you want the date to get parsed from
          :return: file_date: parsed datetime object out of the filename
          """
        try:
            # splits the filename from the prefix to the datetime string
            prefix = self.config().get('main').get('prefix')
            file_to_parse = str(filename).split(prefix)[1].split(".")[0]
            # gets the datetime string and converts it to a datetime object
            file_date = datetime.strptime(str(file_to_parse).replace(";", '').replace('%3A', ':'),
                                          "%Y-%m-%d%" "H:%M:%S")
        except:
            print('error with', filename)
            raise
        return file_date

    def calc_diff_between_dates(self, filedate1, filedate2):
        diff = self.get_file_date(filedate1) - self.get_file_date(filedate2)
        return diff

    def get_files_per_db(self, sorted_files):
        """Gets the files per database and puts them into a dictionary

        :return: files_per_db: dictionary filled with files per database
        """
        files_per_db = {}
        sorted_files = self.sorted_files
        prefix = self.config().get('main').get('prefix')
        # goes through the sorted files
        for filename in sorted_files:
            if prefix not in filename:
                continue
            key_name = filename.split(prefix)[0]
            # if key doesn't exist yet, creates a key with an empty list
            if key_name not in files_per_db:
                files_per_db[key_name] = []
            # if key already exists, adds the filename as value
            files_per_db[key_name].append(filename)

        return files_per_db

    def create_kill_list(self, bucket_start: list, bucket_to_compare: list, hours):
        kill_list = []
        while len(bucket_to_compare) > 1:
            for item in bucket_to_compare:
                diff_start = self.calc_diff_between_dates(bucket_start, item)
                if diff_start < timedelta(hours=hours):
                    kill_list.append(item)
                else:
                    break
            if not kill_list:
                return []
            last = kill_list.pop()
            if last in bucket_to_compare:
                bucket_start = last
                bucket_to_compare = bucket_to_compare[bucket_to_compare.index(last) + 1:]
            else:
                bucket_start = bucket_to_compare.pop(0)

        return kill_list

    def store_files_in_buckets(self, files_per_db):
        raise NotImplementedError()

    def kill_list_size(self, kill_list):
        raise NotImplementedError()

    def total_file_size(self):
        raise NotImplementedError()

    def confirm_delete(self, kill_list):
        raise NotImplementedError()

    def delete_files(self, kill_list):
        raise NotImplementedError()
