import os
from datetime import datetime

# Pseudo Code
'''
    Doorzoek de directory naar files.
        Sorteer de files.
            Pak de laatste file.
                Haal de datum uit de string(filename).
'''


# Doorzoek de directory naar files.
def dir_scan():
    for file in os.listdir("files"):
        print(parse_date(file))


# Haal de datum uit de string(filename).
def parse_date(filename):
    date_parse = {filename: datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d "
                                                                                                            "%H:%M:%S")}
    return date_parse
