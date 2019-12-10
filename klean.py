import os
from datetime import datetime

# Pseudo Code
'''
    Doorzoek de directory naar files.
        Maak een lijst met alle databases daarin.
            Sorteer de files. (SET)
                Pak de laatste file.
                    Haal de datum uit de string(filename).
'''


# Doorzoek de directory naar files.
def dir_scan():
    for file in os.listdir("files"):
        iwannadie

# Haal de datum uit de string(filename).
def parse_date(filename):
    date_parse = {filename: datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d "
                                                                                                            "%H:%M:%S")}
    return date_parse


dir_scan()
