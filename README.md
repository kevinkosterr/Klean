# Klean
> A database backup cleaner. Sorts files by date and deletes the ones you don't need anymore. 
<br>
![RepoSize](https://img.shields.io/github/repo-size/kevinkosterr/Klean)

#### supports:
![BackBlaze](https://www.backblaze.com/pics/backblaze-logo.gif)
<br>

## Usage:

Before using this script please configure it using the provided `config.toml` file. 

### :file_folder:Local

For deleting files locally, the directory must be configured in the `config.toml` file. Please enter the full path , not including the last backslash (if there is one).

### :fire:BackBlaze

For directly using the BackBlaze storage and skipping the confirmation, add -y to the command line. Currently the file size isn't being calculated for BackBlaze Cloud Storage. 

