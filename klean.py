import os
from datetime import datetime

# Bepaal de referentiedatum
'''
    Pak de files
        Sorteer de files.
            Pak de laatste file.
                Haal de datum uit de string(filename).
'''

def parse_date(filename):
    """
        haalt de datum uit een string
    """
    date_parse = datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d %H:%M:%S")
    return date_parse


for file in os.listdir("files"):
    parse_date(file)
