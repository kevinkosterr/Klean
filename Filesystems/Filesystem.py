class Filesystem:

    def get_sorted_files(self):
        raise NotImplementedError()

    def get_file_date(self, filename):
        raise NotImplementedError()

    def calc_diff_between_dates(self, filedate1, filedate2):
        raise NotImplementedError()

    def get_files_per_db(self, sorted_files):
        raise NotImplementedError()

    def create_kill_list(self, bucket_start: list, bucket_to_compare: list, hours):
        raise NotImplementedError()

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