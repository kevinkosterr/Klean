from datetime import datetime, timedelta


class Filesystem:
    def __init__(self):
        self.sorted_files = self.get_sorted_files()
        self.files_per_db = self.get_files_per_db(self.sorted_files)

    def get_sorted_files(self):
        """
        Gets a sorted list of filenames.

            :return: a sorted os.listdir
        """
        raise NotImplementedError()

    def parse_filename_to_date(self, filename):
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
        diff = self.parse_filename_to_date(filedate1) - self.parse_filename_to_date(filedate2)
        return diff

    def get_files_per_db(self, sorted_files):
        """Gets the files per database and puts them into a dictionary

        :return: files_per_db: dictionary filled with files per database
        """
        files_per_db = {}
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
        """ Stores the files in buckets.

        :return: kill_list: list of files to delete
        """
        # files_per_db = self.get_files_per_db(self.get_sorted_files())
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

            this_kill_list.extend(
                self.create_kill_list(bucket1[-1], bucket2,
                                      self.config().get('bucket_second').get('hours_between')))
            if bucket2:
                this_kill_list.extend(
                    self.create_kill_list(bucket2[-1], bucket3,
                                          self.config().get('bucket_third').get('hours_between')))
            if bucket3:
                this_kill_list.extend(
                    self.create_kill_list(bucket3[-1], bucket4,
                                          self.config().get('bucket_fourth').get('hours_between')))
            if bucket4:
                this_kill_list.extend(
                    self.create_kill_list(bucket4[-1], bucket5,
                                          self.config().get('bucket_fifth').get('hours_between')))
            kill_list.extend(this_kill_list)

            print(db_name, 'files found', len(files_per_db[db_name]), '# kill list:', len(this_kill_list))
        return kill_list

    def kill_list_size(self, kill_list):
        raise NotImplementedError()

    def total_file_size(self):
        raise NotImplementedError()

    def confirm_delete(self, kill_list):
        raise NotImplementedError()

    def delete_files(self, kill_list):
        raise NotImplementedError()
