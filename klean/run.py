import os
import toml
import click

from filesystems.localfs import LocalFS
from filesystems.b2fs import B2FS


class KleanError(RuntimeError):
    pass


@click.command()
@click.option('-fs', default='local', help="The filesystem you want to use.")
@click.option('--do-delete', '-del', is_flag=True, help="If you'd like to actually delete the files or not.")
@click.option('--verbose', '-v', is_flag=True, help="Verbose mode.")
def main(fs, do_delete, verbose):
    configuration = toml.load('config.toml')
    if fs == "local":
        my_dir = configuration.get('LocalFS').get('directory')
        fs = LocalFS(my_dir)

    elif fs == "b2":
        bucket = configuration.get('B2Blaze').get('bucket')
        key_id = configuration.get("B2Blaze").get('key_id')
        app_key = configuration.get("B2Blaze").get('app_key')
        fs = B2FS(bucket, key_id, app_key)

    else:
        raise KleanError("Filesystem '%s' is invalid." % fs)

    if not do_delete:
        kill_list = fs.store_files_in_buckets(fs.files_per_db)
        print('\n run Klean with --do-delete or -del to delete the files, run with --verbose to see all filenames '
              'and whether they will be deleted.')
        if verbose:
            for filename in fs.sorted_files:
                print(filename, filename in kill_list)
        return

    else:
        kill_list = fs.store_files_in_buckets(fs.files_per_db)
        fs.delete_files(kill_list)


if __name__ == '__main__':
    # TODO: build support for more cloud based services.
    main()
