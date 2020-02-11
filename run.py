import toml
import sys
from Filesystems.LocalFS import LocalFS
from Filesystems.B2FS import B2FS
import pprint

# class SshFS(Filesystem):
#
#     "details ingevuld met gebruik van plumbum"
#
# class Fs2FS(Filesystem):
#     "details ingevul met gebruik van een willekeurig FS2 filesystem"


if __name__ == '__main__':
    c = toml.load('config.toml')
    # the following variables can be configured in the config.toml file
    # my_dir, bucket_name, key_id, app_id, folder
    my_dir = c.get('LocalFS').get('directory')
    bucket_name = c.get('B2Blaze').get('bucket')
    key_id = c.get('B2Blaze').get('key_id')
    app_id = c.get('B2Blaze').get('app_id')
    folder = c.get('B2Blaze').get('folder')
    skip = False

    # if -y is given as an argument, it skips the confirmation
    if '-y' in sys.argv:
        skip = True

    # if --do-delete is not given, it will only print out which
    # which files it was going to delete if you were to run the program
    if '--do-delete' not in sys.argv:
        fs = B2FS(bucket_name, key_id, app_id)
        killist = fs.store_files_in_buckets(fs.files_per_db)
        for filename in fs.sorted_files:
            print(filename, filename in killist)
        # pprint.pprint(killist)

        exit()

    if not skip:
        print("Choose a filesystem: LocalFS | B2FS")
        fs = input("")
        if fs == 'LocalFS':
            fs = LocalFS(my_dir)
        if fs == 'B2FS':
            try:
                fs = B2FS(bucket_name, key_id, app_id)
            except (ValueError, Exception):
                fs = B2FS(bucket_name, key_id, app_id, folder)

    sorted_files = fs.sorted_files
    kill_list = fs.store_files_in_buckets(fs.files_per_db)
    for filename in fs.sorted_files:
        print(filename, filename in kill_list)
    if skip:
        fs.delete_files(kill_list)
    else:
        fs.confirm_delete(kill_list)
