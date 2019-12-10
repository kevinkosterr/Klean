import os
from datetime import datetime

# Bepaal de referentiedatum
'''
    Haal alle bestanden op en bepaal de datum die bij die bestanden hoort door ze uit de naam te halen.
'''


def parse_date(filename):
    """
        haalt de datum uit een string
    """
    date_parse = datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d %H:%M:%S")
    return date_parse


for file in os.listdir("files"):
    parse_date(file)
