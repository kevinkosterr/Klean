import toml
import sys
from Filesystems.LocalFS import LocalFS

# class SshFS(Filesystem):
#
#     "details ingevuld met gebruik van plumbum"
#
# class Fs2FS(Filesystem):
#     "details ingevul met gebruik van een willekeurig FS2 filesystem"


if __name__ == '__main__':
    c = toml.load('config.toml')
    my_dir = c.get('LocalFS').get('directory')
    bucket_name = c.get('B2Blaze').get('bucket')
    if not my_dir:
        print("You have not set a working directory yet. \nA directory can be set in config.toml")
        exit(1)
    if len(sys.argv) < 2:
        print("Choose a filesystem: LocalFS | B2FS")
        fs = input("")
        if fs == 'LocalFS':
            fs = LocalFS(my_dir)

    sorted_files = fs.sorted_files
    kill_list = fs.store_files_in_buckets(fs.files_per_db)
    fs.confirm_delete(kill_list)
