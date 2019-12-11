import json
import os
from datetime import datetime

d = {}

# sorteert de files en zet ze in een dictionary
for file in sorted(os.listdir("files")):
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
    date_parse = datetime.strptime(filename, "%Y-%m-%d%" "H:%M:%S")
    return date_parse


# haalt de values uit de dictionary en parsed de date uit de namen
for db_name in d:
    for f_name in d.values():
    #     values_string = str(f_name).split("+")[1].replace(';', '').replace('%3A', ':').split("]")[1]
    # print(parse_date(values_string))
