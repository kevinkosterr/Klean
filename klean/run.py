import toml
import click

from filesystems.localfs import LocalFS
from filesystems.b2fs import B2FS


class KleanError(RuntimeError):
    pass


@click.command()
@click.option('-fs', default='local', help="The filesystem you want to use.")
@click.option('--do-delete', '-del', is_flag=True, help="If you'd like to actually delete the files or not.")
def main(fs, do_delete):
    c = toml.load('data/config.toml')
    if fs == "local":
        my_dir = c.get('LocalFS').get('directory')
        fs = LocalFS(my_dir)

    elif fs == "b2":
        bucket = c.get('B2Blaze').get('bucket')
        key_id = c.get("B2Blaze").get('key_id')
        app_key = c.get("B2Blaze").get('app_key')
        fs = B2FS(bucket, key_id, app_key)

    else:
        raise KleanError("Filesystem '%s' is invalid." % fs)

    if not do_delete:
        kill_list = fs.store_files_in_buckets(fs.files_per_db)
        for filename in fs.sorted_files:
            print(filename, filename in kill_list)
        return

    else:
        sorted_files = fs.sorted_files
        kill_list = fs.store_files_in_buckets(fs.files_per_db)


if __name__ == '__main__':
    # TODO: build support for more cloud based services.
    # TODO: refactor all of the code.
    # TODO: change the way the CLI is handled in the code.
    main()
