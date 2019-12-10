import os
from datetime import datetime

d = {}

for file in sorted(os.listdir("files")):
    naam = file.split('+')[0]
    if naam not in d:
        d[naam] = []
    d[naam].append(file)


# Haal de datum uit de string(filename).
def parse_date(filename):
    """
        haalt de datum uit de filename
    """
    date_parse = {filename: datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d "
                                                                                                            "%H:%M:%S")}
    return date_parse
