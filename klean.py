import toml
import os
from datetime import datetime, timedelta

config = toml.load('config.toml')

d = {}

# os.listdir("files")
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
    """
    EN:
    gets the datetime object out of the filename

    NL:
    haalt het datetime object uit de filename
    """
    # file_parsed = datetime.strptime(filename, "%Y-%m-%d%" "H:%M:%S")
    # return file_parsed
    try:
        file_to_parse = str(filename).split("+")[1].split(".")[0]
        parsed_file = datetime.strptime(str(file_to_parse).replace(";", '').replace('%3A', ':'), "%Y-%m-%d%" "H:%M:%S")
    except:
        print('error with ', filename)
        raise
    return parsed_file


def process_bucket(start_point, list_to_compare, hours):
    """
    EN:
    calculates the difference between the starting point and the next item, where the next item is first in the next
    list. paramater 'hours' defines how big the gap between the back-ups is allowed to be.

    NL:
    rekent het verschil tussen het startpunt en het volgende item, paramater hours geeft aan hoeveel uren
    er maximaal tussen elke back-up mag zitten.
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
    kill_list.extend(this_kill_list)
    print(db_name, 'files found', len(d[db_name]), '# kill list:', len(this_kill_list))

file_size = os.path.getsize(config.get('main').get('directory'))

print('-------------------------------------------')
print('total file size:', float(file_size * 0.000001), 'MB')
print('amount of files that will be deleted:', len(kill_list))
# print('total file size of files to delete:', int(del_size*0.000001), 'MB')

control = input("Would you like to delete these files? (y/n): ")
if control == "y":
    pass
else:
    exit()

my_dir = config.get('main').get('directory')
del_list = []
for filename in os.listdir(my_dir):
    if filename in kill_list:
        os.remove(os.path.join(my_dir, filename))
        del_list.extend(filename)
        print(filename, 'deleted.')
print(len(del_list), "files have been deleted")

# keep_list = [_ for _ in d[db_name] if _ not in kill_list]
# # print(keep_list)
# for idx, filename in enumerate(keep_list[:-1]):
#     print(idx, parse_date(filename) - parse_date(keep_list[idx + 1]), filename)
