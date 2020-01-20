import toml
import sys
from Filesystems.LocalFS import LocalFS
from Filesystems.B2FS import B2FS


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
    key_id = c.get('B2Blaze').get('key_id')
    app_id = c.get('B2Blaze').get('app_id')
    folder = c.get('B2Blaze').get('folder')
    if len(sys.argv) < 2:
        print("Choose a filesystem: LocalFS | B2FS")
        fs = input("")
        if fs == 'LocalFS':
            fs = LocalFS(my_dir)
        if fs == 'B2FS':
            try:
                fs = B2FS(bucket_name,  key_id, app_id)
            except:
                fs = B2FS(bucket_name,  key_id, app_id, folder)

    sorted_files = fs.sorted_files
    kill_list = fs.store_files_in_buckets(fs.files_per_db)
    fs.confirm_delete(kill_list)