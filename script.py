import toml
import os
from datetime import datetime, timedelta
import cProfile


# get a sorted list of files
def get_sorted_files():
    sorted_files = sorted(os.listdir(config.get('main').get('directory')), reverse=True)
    # return a reverse sorted file list
    return sorted_files


def calc_diff_between_dates(filedate1, filedate2):
    diff = get_file_date(filedate1) - get_file_date(filedate2)
    return diff


def get_files_per_db():
    """Gets the files per database and puts them into a dictionary

    :return: files_per_db: dictionary filled with files per database
    """
    files_per_db = {}
    sorted_files = get_sorted_files()
    # goes through the sorted os.listdir
    for filename in sorted_files:
        if f"{config.get('main').get('prefix')}" not in filename:
            continue
        # TODO: make the prefix configurable
        key_name = filename.split(f"{config.get('main').get('prefix')}")[0]
        # if key doesn't exist yet, creates a key with an empty list
        if key_name not in files_per_db:
            files_per_db[key_name] = []
        # if key already exists, adds the filename as value
        files_per_db[key_name].append(filename)

    return files_per_db


def get_file_date(filename):
    """ Gets the datetime object from a filename

    :param filename: the filename of which you want the date to get parsed from
    :return: file_date: parsed datetime object out of the filename
    """
    try:
        # splits the filename from the prefix to the datetime string
        file_to_parse = str(filename).split("+")[1].split(".")[0]
        # gets the datetime string and converts it to a datetime object
        file_date = datetime.strptime(str(file_to_parse).replace(";", '').replace('%3A', ':'), "%Y-%m-%d%" "H:%M:%S")
    except:
        print('error with', filename)
        raise
    return file_date


def create_kill_list(bucket_start: list, bucket_to_compare: list, hours):
    kill_list = []
    while len(bucket_to_compare) > 1:
        for item in bucket_to_compare:
            diff_start = calc_diff_between_dates(bucket_start, item)
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


def store_files_in_buckets():
    """ Stores the files in buckets, uses

    :return: kill_list: list of files to delete
    """
    files_per_db = get_files_per_db()
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
            diff = calc_diff_between_dates(first_element, cursor)
            # Period in days is configurable.
            # If difference is smaller than or the same as period in days in config.toml
            # append it to the first bucket.
            if diff <= timedelta(days=config.get('bucket_first').get('period_in_days')):
                bucket1.append(cursor)
            # If difference is smaller as the period in days append to the second bucket.
            elif diff < timedelta(days=config.get('bucket_second').get('period_in_days')):
                bucket2.append(cursor)
            elif diff < timedelta(days=config.get('bucket_third').get('period_in_days')):
                bucket3.append(cursor)
            elif diff < timedelta(days=config.get('bucket_fourth').get('period_in_days')):
                bucket4.append(cursor)
            elif diff >= timedelta(days=config.get('bucket_fifth').get('period_in_days')):
                bucket5.append(cursor)

        this_kill_list.extend(create_kill_list(bucket1[-1], bucket2, config.get('bucket_second').get('hours_between')))
        this_kill_list.extend(create_kill_list(bucket2[-1], bucket3, config.get('bucket_third').get('hours_between')))
        this_kill_list.extend(create_kill_list(bucket3[-1], bucket4, config.get('bucket_fourth').get('hours_between')))
        this_kill_list.extend(create_kill_list(bucket4[-1], bucket5, config.get('bucket_fifth').get('hours_between')))
        kill_list.extend(this_kill_list)

        print(db_name, 'files found', len(files_per_db[db_name]), '# kill list:', len(this_kill_list))

    return kill_list


def kill_list_size(kill_list):
    kill_list_size = 0
    for filename in kill_list:
        file_size = os.path.getsize(f"{config.get('main').get('directory')}\\{filename}")
        kill_list_size += file_size
    return kill_list_size


def total_size_files():
    total_size = sum(os.path.getsize(f) for f in os.listdir(config.get('main').get('directory')) if os.path.isfile(f))
    return total_size


def confirm_delete(kill_list):
    delete_file_size = round(float(kill_list_size(kill_list) * 0.000001), 3)
    total_size = round(float(total_size_files() * 0.000001), 3)
    print(f'\ntotal file size of files in directory: {total_size} MB')
    print(f'# kill list file size: {delete_file_size} MB')
    confirm = input("\nAre you sure you want to delete these files? (y/n) ")
    if confirm == 'y':
        delete_files(kill_list)
    if confirm == 'n':
        print('Ok.')
    else:
        confirm_delete(kill_list)


def delete_files(kill_list):
    file_dir = config.get('main').get('directory')
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


if __name__ == '__main__':
    config = toml.load('config.toml')
    sorted_files = get_sorted_files()
    kill_list = store_files_in_buckets()
    # # cProfile.run('store_files_in_buckets()', sort='time')
    confirm_delete(kill_list)
