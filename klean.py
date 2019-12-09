import os
import json
from datetime import datetime

# 1. referentiedatum halen uit de filenames van de back-ups
"""
    alle files hebben een datum in de naam, dit word de referentiedatum. er vinden 168 back-ups per week plaats.
"""

config = open("config.json")
c = json.load(config)
ref_date = os.listdir(c['path'])[0]


def parse_date(filename):
    '''
        gets the date from a file name
    '''
    date_parse = datetime.strptime(filename.split('+')[1].replace("%3A", ":").replace(";", " "), "%Y-%m-%d %H:%M:%S")
    return date_parse


for file in os.listdir(c['path']):
    print(file)
    print(parse_date(file))

# 2. het verwijderen vanaf die datum voor de tweede week
"""
    tussen deze back-ups mag maximaal 4,5 uur per keer zitten. van de 168 blijven er dus 42 over.
"""

# 3. bepaal het volgende startpunt
"""
    het volgende startpunt is waar de laatste week geëindigd is. 
"""
