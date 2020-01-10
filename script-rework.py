import toml
import os
from datetime import datetime, timedelta


# read the config file
def read_config(subject, instance):
    config = toml.load('config.toml')
    return config.get(subject).get(instance)


# get a sorted list of files
def get_sorted_files():
    sorted_files = sorted(os.listdir(read_config('main', 'directory')), reverse=True)
    # return a reverse sorted file list
    return sorted_files


def files_per_db():
    files_per_db = {}
    sorted_files = get_sorted_files()
    for filename in sorted_files:
        if '+' not in filename:
            continue
        elif '+' in filename:
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


def kill_list_create(start_point, list_to_compare, hours):
    kill_list = []
    while len(list_to_compare) > 1:
        for item in list_to_compare:
            diff_start = get_file_date(start_point) - get_file_date(item)
            if diff_start < timedelta(hours=hours):
                kill_list.append(item)
            else:
                break
        if not kill_list:
            return []
        last = kill_list.pop()
        if last in list_to_compare:
            start_point = last
            list_to_compare = list_to_compare[list_to_compare.index(last) + 1:]
        else:
            start_point = list_to_compare.pop(0)

    return kill_list


def process_bucket():
    kill_list = []
    db_files = files_per_db()
    for db_name in db_files.keys():
        this_kill_list = []
        bucket1 = []
        bucket2 = []
        bucket3 = []
        bucket4 = []
        bucket5 = []
        first_element = db_files[db_name][0]
        for cursor in db_files[db_name]:
            diff = get_file_date(first_element) - get_file_date(cursor)
            # first bucket, period in days is defined in config file. standard is 7
            if diff <= timedelta(read_config('bucket_first', 'period_in_days')):
                # appends to the bucket
                bucket1.append(cursor)
            # second bucket, period in days is defined in config file. standard is 15
            elif diff < timedelta(read_config('bucket_second', 'period_in_days')):
                bucket2.append(cursor)
            # third bucket, period in days is defined in config file. standard is 29
            elif diff < timedelta(read_config('bucket_third', 'period_in_days')):
                bucket3.append(cursor)
            # fourth bucket, period in days is defined in config file. standard is 85
            elif diff < timedelta(read_config('bucket_fourth', 'period_in_days')):
                bucket4.append(cursor)
            # fifth bucket, period in days is defined in config file. standard is 85
            elif diff >= timedelta(read_config('bucket_fifth', 'period_in_days')):
                bucket5.append(cursor)

        this_kill_list.extend(kill_list_create(bucket1[-1], bucket2, read_config('bucket_second', 'hours_between')))
        this_kill_list.extend(kill_list_create(bucket2[-1], bucket3, read_config('bucket_third', 'hours_between')))
        this_kill_list.extend(kill_list_create(bucket3[-1], bucket4, read_config('bucket_fourth', 'hours_between')))
        this_kill_list.extend(kill_list_create(bucket4[-1], bucket5, read_config('bucket_fifth', 'hours_between')))
        # extends kill_list with every this_kill_list to create one kill_list
        kill_list.extend(this_kill_list)
        # prints the amount of files for every database and how many items will be deleted
        # print(db_name, 'files found', len(db_files[db_name]), '# kill list:', len(this_kill_list))
        return this_kill_list


def show_amount_of_files():
    db_files = files_per_db()
    this_kill_list =
    for db_name in db_files.keys():
        print(db_name, 'files found', len(db_files[db_name]), '# kill list:', len(this_kill_list))
    print(round(float(file_size() * 0.00001), 3), 'MB')


def file_size():
    return sum(os.path.getsize(f) for f in os.listdir(read_config('main', 'directory')) if os.path.isfile(f))


def confirm_del():
    confirm = input("Are you sure you want to delete these files? (y/n) ")
    if not confirm == 'y':
        if not confirm == 'n':
            confirm_del()
    if confirm == 'y':
        del_files()
    if confirm == 'n':
        print("Ok.")


def del_files():
    my_dir = read_config('main', 'directory')
    for filename in os.listdir(my_dir):
        if filename in kill_list:
            os.remove(os.path.join(my_dir, filename))
            print(filename, 'removed')
        print('All files have been deleted succesfully.')


if __name__ == '__main__':
    process_bucket()
    show_amount_of_files()
    confirm_del()
