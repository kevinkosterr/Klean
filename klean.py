import os
from datetime import datetime

d = {}

# sorteert de files en zet ze in een dictionary
for file in sorted(os.listdir("files")):
    naam = file.split('+')[0]
    # als de naam niet in de dictionary voorkomt, maak dan een sleutel en geef 'm een lege lijst
    if naam not in d:
        d[naam] = []
    d[naam].append(file)
# os.listdir is hier al gesorteerd


# Haal de datum uit de string(filename).
def parse_date(filename):
    """
        haalt de datum uit de filename
    """
    date_parse = {filename: datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d "
                                                                                                            "%H:%M:%S")}
    return date_parse
