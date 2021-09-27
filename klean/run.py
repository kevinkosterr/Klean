import toml
import sys
from filesystems.localfs import LocalFS
from filesystems.b2fs import B2FS

if __name__ == '__main__':
    c = toml.load('data/config.toml')
    # the following variables can be configured in the config.toml file
    # my_dir, bucket_name, key_id, app_id, folder
    my_dir = c.get('LocalFS').get('directory')
    bucket_name = c.get('B2Blaze').get('bucket')
    key_id = c.get('B2Blaze').get('key_id')
    app_id = c.get('B2Blaze').get('app_id')
    skip = False

    # if -y is given as an argument, it skips the confirmation
    if '-y' in sys.argv:
        skip = True
    # picks b2fs if b2 is given as an argument
    if 'b2' in sys.argv[1]:
        fs = B2FS(bucket_name, key_id, app_id)
    # picks localfs if local is given as an argument
    if 'local' in sys.argv[1]:
        fs = LocalFS(my_dir)

    # if --do-delete is not given, it will only print out which
    # which files it was going to delete if you were to run the program
    if '--do-delete' not in sys.argv:
        try:
            killlist = fs.store_files_in_buckets(fs.files_per_db)
        # raises a NameError and prints error
        # if no filesystem is given
        except NameError:
            print('Filesystem {b2, local} must be passed as the first argument')
            raise
        for filename in fs.sorted_files:
            print(filename, filename in killlist)
        exit()

    try:
        sorted_files = fs.sorted_files
        kill_list = fs.store_files_in_buckets(fs.files_per_db)
    # raises a NameError and prints error
    # if no filesystem is given
    except NameError:
        print('Filesystem {b2, local} must be passed as the first argument')
        raise
    if skip:
        fs.delete_files(kill_list)
    else:
        fs.confirm_delete(kill_list)
