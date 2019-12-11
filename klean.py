import json
import os
from datetime import datetime

d = {}

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
    date_parse = datetime.strptime(filename, "%Y-%m-%d%" "H:%M:%S")
    return date_parse


# haalt de values uit de dictionary en parsed de date uit de namen
# zoekt in de dictionary naar elke databasename
for db_name in d:
    print(db_name)
    # zoekt elke value in de keys
    for values in d[db_name]:
        values = str(values).split("+")[1]
        parsed_values = parse_date(values.replace(";", '').replace('%3A', ':'))
        print(parsed_values)
