import os
import json

# 1. referentiedatum halen uit de filenames van de back-ups
"""
    alle files hebben een datum in de naam, dit word de referentiedatum. er vinden 168 back-ups per week plaats.
"""

# os.listdir(path)[0] - selecteert het eerste bestand uit de path
config = open("config.json")
c = json.load(config)

first_file = os.listdir(c['path'])[0]

print(first_file.split('+')[1].replace("%3A", ":").replace(";", " "))

# 2. het verwijderen vanaf die datum voor de tweede week
"""
    tussen deze back-ups mag maximaal 4,5 uur per keer zitten. van de 168 blijven er dus 42 over.
"""

# 3. bepaal het volgende startpunt
"""
    het volgende startpunt is waar de laatste week geëindigd is. 
"""
