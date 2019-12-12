import json
import os
from datetime import datetime, timedelta

d = {}
kill_list = []

# sorteert de files en zet ze in een dictionary
for file in sorted(os.listdir("files"), reverse=True):
    key_name = file.split('+')[0]
    # als de naam niet in de dictionary voorkomt, maak dan een sleutel en geef 'm een lege lijst
    if key_name not in d:
        d[key_name] = []
    d[key_name].append(file)
# os.listdir is hier al gesorteerd


# haal de datum uit de string(filename).
def parse_date(filename):
    """
        haalt de datum uit de filename
    """
    # file_parsed = datetime.strptime(filename, "%Y-%m-%d%" "H:%M:%S")
    # return file_parsed
    file_to_parse = str(filename).split("+")[1]
    parsed_file = datetime.strptime(file_to_parse.replace(";", '').replace('%3A', ':'), "%Y-%m-%d%" "H:%M:%S")
    return parsed_file


def process_bucket(startpoint, list_to_compare, hours):
    for item in list_to_compare:
        diff_start = parse_date(startpoint) - parse_date(item)
        if diff_start < timedelta(hours=hours):
            kill_list.append(item)
    kill_list.pop()


for db_name in d.keys():
    bucket1 = []  # week 1
    bucket2 = []  # week 2
    bucket3 = []  # week 3 t/m 4
    bucket4 = []  # week 5 t/m 12
    bucket5 = []  # alles na week 12
    a = d[db_name][0]
    for cursor in d[db_name]:
        diff = parse_date(a) - parse_date(cursor)
        if diff <= timedelta(days=7):
            bucket1.append(cursor)
        elif diff < timedelta(days=15):
            bucket2.append(cursor)
        elif diff < timedelta(days=29):
            bucket3.append(cursor)
        elif diff < timedelta(days=85):
            bucket4.append(cursor)
        elif diff >= timedelta(days=85):
            bucket5.append(cursor)

    process_bucket(bucket1[-1], bucket2, 4.5)

# haalt de values uit de dictionary en parsed de date uit de namen
# zoekt in de dictionary naar elke databasename
# for db_name in d:
#     # zoekt elke value in de keys
#     for values in d[db_name]:
#         values = str(values).split("+")[1]
#         parsed_values = parse_date(values.replace(";", '').replace('%3A', ':'))
#         print(parsed_values)
