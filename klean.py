import os
from datetime import datetime

# Bepaal de referentiedatum
'''
    Doorzoek de directory voor files.
        Sorteer de files.
            Pak de laatste file.
                Haal de datum uit de string(filename).
'''

# Haal de datum uit de string(filename).
def parse_date(filename):
    date_parse = {filename: datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d "
                                                                                                            "%H:%M:%S")}
    return date_parse


# Doorzoekt de directory voor files.
for file in os.listdir("files"):
    print(parse_date(file))
