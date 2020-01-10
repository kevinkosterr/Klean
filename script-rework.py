import toml
import os
from datetime import datetime, timedelta
import cProfile


# sets the config file
def set_config(subject, instance):
    config = toml.load('config.toml')
    return config.get(subject).get(instance)


# get a sorted list of files
def get_sorted_files():
    sorted_files = sorted(os.listdir(set_config('main', 'directory')), reverse=True)
    # return a reverse sorted file list
    return sorted_files


def calc_diff_between_dates(filedate1, filedate2):
    diff = get_file_date(filedate1) - get_file_date(filedate2)
    return diff


# get the files per database, puts them in dictionary
def get_files_per_db():
    files_per_db = {}
    sorted_files = get_sorted_files()
    for filename in sorted_files:
        if '+' not in filename:
            continue
        # elif '+' in filename:
        key_name = filename.split('+')[0]
        if key_name not in files_per_db:
            files_per_db[key_name] = []
        files_per_db[key_name].append(filename)

    return files_per_db


# gets the datetime object from a filename
def get_file_date(filename):
    try:
        file_to_parse = str(filename).split("+")[1].split(".")[0]
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


# create buckets, fill them with the files per database
def store_files_in_buckets():
    files_per_db = get_files_per_db()
    kill_list = []
    for db_name in files_per_db.keys():
        this_kill_list = []
        bucket1 = []
        bucket2 = []
        bucket3 = []
        bucket4 = []
        bucket5 = []
        first_element = files_per_db[db_name][0]
        for cursor in files_per_db[db_name]:
            diff = calc_diff_between_dates(first_element, cursor)
            if diff <= timedelta(days=set_config('bucket_first', 'period_in_days')):
                bucket1.append(cursor)
            elif diff < timedelta(days=set_config('bucket_second', 'period_in_days')):
                bucket2.append(cursor)
            elif diff < timedelta(days=set_config('bucket_third', 'period_in_days')):
                bucket3.append(cursor)
            elif diff < timedelta(days=set_config('bucket_fourth', 'period_in_days')):
                bucket4.append(cursor)
            elif diff >= timedelta(days=set_config('bucket_fifth', 'period_in_days')):
                bucket5.append(cursor)

        this_kill_list.extend(create_kill_list(bucket1[-1], bucket2, set_config('bucket_second', 'period_in_days')))
        this_kill_list.extend(create_kill_list(bucket2[-1], bucket3, set_config('bucket_third', 'period_in_days')))
        this_kill_list.extend(create_kill_list(bucket3[-1], bucket4, set_config('bucket_fourth', 'period_in_days')))
        this_kill_list.extend(create_kill_list(bucket4[-1], bucket5, set_config('bucket_fifth', 'period_in_days')))
        kill_list.extend(this_kill_list)

        print(db_name, 'files found', len(files_per_db[db_name]), '# kill list:', len(this_kill_list))

    confirm_delete()


# def show_kill_list():
#     return

# def file_size():
#     return


def confirm_delete():
    confirm = input("Are you sure you want to delete these files? (y/n) ")
    if confirm == 'y':
        delete_files()
    if confirm == 'n':
        print('Ok.')
    else:
        confirm_delete()


if __name__ == '__main__':
    cProfile.run('store_files_in_buckets()', sort='time')

