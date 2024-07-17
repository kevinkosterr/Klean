import json
import os

with open(os.path.join(os.getcwd(), 'data', 'files_fixture.json'), 'r') as file:
    file_names = json.loads(file.read())

for file_name in file_names:

    files_path = os.path.join(os.getcwd(), 'files')

    if not os.path.exists(files_path):
        os.makedirs(files_path)

    path = os.path.join(files_path, file_name)
    with open(path, "w") as f:
        f.write(file_name[0])