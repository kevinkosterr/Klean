# Creating a filesystem plugin
This guide will walk you through the process of creating a custom filesystem plugin for Klean. 
By following these steps, you can extend Klean's functionality to support additional storage systems or data sources.

## 1. Import the required modules
```python
from klean.plugins import FileSystemPlugin
```

## 2. Define a filesystem class
```python
# src/my_filesystem/__init__.py
class MyFileSystem(FileSystemPlugin):
    name = "foo" # This is the name of the filesystem within the commandline, which will run like `klean foo`
    help = "This is a custom filesystem plugin for Klean."
```

## 3. Read from configuration
Use the plugin configuration to load any required settings, such as a directory path, or API key.
This uses the standard [`tomllib`](https://docs.python.org/3/library/tomllib.html) (Python 3.11+) library to read configuration values from a TOML file.
```python
# src/my_filesystem/__init__.py
class MyFileSystem(FileSystemPlugin):
    # ....

    def __init__(self, config: dict):
        self.api_key = config.get('myFS').get('api_key') # config.get(YOUR_SECTION).get(YOUR_OPTION)
        super().__init__(config)

```

## 4. Implement file listing
Your filesystem plugin should provide a method that returns a sorted list of filenames.
```python
# src/my_filesystem/__init__.py
# import ...
import requests

class MyFileSystem(FileSystemPlugin):
    # other code omitted...

    def get_sorted_filenames(self):
        # Assuming the API returns only a list of filenames here.
        filenames = requests.get('https://example-api.com/filenames').json()
        return sorted(filenames, reverse=True)
```

## 5. Implement file deletion
```python
# src/my_filesystem/__init__.py
# imports omitted...

class MyFileSystem(FileSystemPlugin):
    # other code omitted...

    def delete_files(self, to_delete, _verbose):
        deleted_files = []
        for filename in to_delete:
            response = requests.delete(f"https://example-api.com/file/{filename}")
            if response.status_code == 200:
                deleted_files.append(filename)
        print(f"{len(deleted_files)} succesfully deleted.")
```

## 6. Add an entry point
In order for Klean to find the plugin after it has been installed, you need to add an entry point to your `setup.py` or 
`pyproject.toml` within the `klean.plugins` group. With `uv` you can do this like so:
```toml
# pyproject.toml
[project.entry-points."klean.plugins"]
myfs = "my_filesystem:MyFileSystem"
```

## 7. Done
You are now ready to use your custom filesystem plugin with Klean. It should be installed in the same environment as Klean so
that Klean can find the plugin and use it.

## Full code example

```python
# src/my_filesystem/__init__.py
import requests
from klean.plugins import FileSystemPlugin

class MyFileSystem(FileSystemPlugin):
    name = "foo" # This is the name of the filesystem within the commandline, which will run like `klean foo`
    help = "This is a custom filesystem plugin for Klean."

    def __init__(self, config: dict):
        self.api_key = config.get('myFS').get('api_key') # config.get(YOUR_SECTION).get(YOUR_OPTION)
        super().__init__(config)

    def get_sorted_filenames(self):
        # Assuming the API returns only a list of filenames here.
        filenames = requests.get('https://example-api.com/filenames', 
                                 headers={"Authorization": f"ApiKey {self.api_key}"}).json()
        return sorted(filenames, reverse=True)

    def delete_files(self, to_delete, _verbose):
        deleted_files = []
        for filename in to_delete:
            response = requests.delete(
                f"https://example-api.com/file/{filename}",
                headers={"Authorization": f"ApiKey {self.api_key}"}
            )
            if response.status_code == 200:
                deleted_files.append(filename)
        print(f"{len(deleted_files)} succesfully deleted.")
```






