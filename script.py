"""
A script that deletes back-ups within a certain period of time.

Certain parts of this script can be configured using the config.toml file.
"""
import toml
import os
from datetime import datetime, timedelta

config = toml.load('config.toml')

d = {}

# sorts the files and puts them in a dictionary
for filename in sorted(os.listdir(config.get('main').get('directory')), reverse=True):
    if '+' not in filename:
        continue
    key_name = filename.split('+')[0]
    # if the name is not in the dictionary, create a key with an empty list as value
    if key_name not in d:
        d[key_name] = []
    d[key_name].append(filename)


# the filenames have already been sorted from here.


def parse_date(filename):
    """ Gets the datetime object out of a filename

        Parameters:
            filename (str) : the filename that contains a datetime object in string

        Returns:
            parsed_file (datetime object) : the datetime object from filename

    """
    try:
        file_to_parse = str(filename).split("+")[1].split(".")[0]
        parsed_file = datetime.strptime(str(file_to_parse).replace(";", '').replace('%3A', ':'), "%Y-%m-%d%" "H:%M:%S")
    except:
        print('error with ', filename)
        raise
    return parsed_file


def process_bucket(start_point, list_to_compare, hours):
    """ Calculates the difference between the starting point of one bucket and the first of the next bucket.

        Parameters:
            start_point (list) : the first bucket, used as starting point
            list_to_compare (list) : the bucket that needs to be compared to the start_point
            hours (float) : the amount of hours there is allowed to be between each back-up, defined in config.toml

        Returns:
            kill_list (list) : a list of files that will be deleted
    """
    kill_list = []
    while len(list_to_compare) > 1:
        for item in list_to_compare:
            diff_start = parse_date(start_point) - parse_date(item)
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


kill_list = []
for db_name in d.keys():
    this_kill_list = []
    bucket1 = []
    bucket2 = []
    bucket3 = []
    bucket4 = []
    bucket5 = []
    a = d[db_name][0]
    for cursor in d[db_name]:
        diff = parse_date(a) - parse_date(cursor)
        # first bucket, period in days is defined in config file. standard is 7
        if diff <= timedelta(days=config.get('bucket_first').get('period_in_days')):
            # appends to the bucket
            bucket1.append(cursor)
        # second bucket, period in days is defined in config file. standard is 15
        elif diff < timedelta(days=config.get('bucket_second').get('period_in_days')):
            bucket2.append(cursor)
        # third bucket, period in days is defined in config file. standard is 29
        elif diff < timedelta(days=config.get('bucket_third').get('period_in_days')):
            bucket3.append(cursor)
        # fourth bucket, period in days is defined in config file. standard is 85
        elif diff < timedelta(days=config.get('bucket_fourth').get('period_in_days')):
            bucket4.append(cursor)
        # fifth bucket, period in days is defined in config file. standard is 85
        elif diff >= timedelta(days=config.get('bucket_fifth').get('period_in_days')):
            bucket5.append(cursor)

    this_kill_list.extend(process_bucket(bucket1[-1], bucket2, config.get('bucket_second').get('hours_between')))
    this_kill_list.extend(process_bucket(bucket2[-1], bucket3, config.get('bucket_third').get('hours_between')))
    this_kill_list.extend(process_bucket(bucket3[-1], bucket4, config.get('bucket_fourth').get('hours_between')))
    this_kill_list.extend(process_bucket(bucket4[-1], bucket5, config.get('bucket_fifth').get('hours_between')))
    # extends kill_list with every this_kill_list to create one kill_list
    kill_list.extend(this_kill_list)
    # prints the amount of files for every database and how many items will be deleted
    print(db_name, 'files found', len(d[db_name]), '# kill list:', len(this_kill_list))


# def get_del_file_size():
#     my_dir = config.get('main').get('directory')
#     delete_size = 0
#     for f in os.listdir(my_dir):
#         if f in kill_list:
#             os_path = my_dir, '/', f
#             path_size = ''.join(os_path)
#             delete_size += os.path.getsize(path_size)
#     return delete_size


def get_file_size():
    """" Returns total size of files in directory

        Returns:
            total_size(int) : the total size of all files in the given directory

    """
    total_size = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
    return total_size
    # file_size = os.path.getsize(config.get('main').get('directory'))
    #
    # print('-------------------------------------------')
    # print('total file size:', float(file_size * 0.000001), 'MB')
    # print('amount of files that will be deleted:', len(kill_list))


def p_file_size():
    """" Prints the file size of the result of get_file_size()
    """
    print('-------------------------------------------')
    print('total file size: ', round(float(get_file_size() * 0.000001), 3), 'MB')
    # print('delete file size: ', round(float(get_del_file_size() * 0.000001), 3), 'MB')


p_file_size()


def delete_files():
    """" Deletes the files in kill_list
    """
    my_dir = config.get('main').get('directory')
    # del_list = []
    for filename in os.listdir(my_dir):
        if filename in kill_list:
            os.remove(os.path.join(my_dir, filename))
            print('[', parse_date(filename), ']', filename, 'deleted.')
        # keep_list = [_ for _ in d[db_name] if _ not in kill_list]
        # # print(keep_list)
        # for idx, filename in enumerate(keep_list[:-1]):
        #     print(idx, parse_date(filename) - parse_date(keep_list[idx + 1]), filename)


def safety_measure():
    """" Prevents deleting files before confirmation
    """
    control = input("Would you like to delete these files? (y/n): ")
    if not control == 'y':
        if not control == 'n':
            print('Invalid. (y/n)')
            safety_measure()
    if control == 'n':
        exit()
    if control == 'y':
        delete_files()


safety_measure()
