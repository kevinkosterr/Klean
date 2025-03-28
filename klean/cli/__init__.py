import click
import os
import toml

from klean.filesystems import Filesystem
from klean.helpers import get_file_system

from typing import List

filesystem_choices: click.Choice = click.Choice(["local", "b2"])

@click.command()
@click.option('-fs', default='local', help="The filesystem you want to use.", type=filesystem_choices)
@click.option('--generate-files', '-g', is_flag=True, help="Generates local files for testing, ignores all other options")
@click.option('--do-delete', '-del', is_flag=True, help="Required to actually delete files.")
@click.option('--config', '-c', type=click.Path(exists=True), help="The config file to use. Will try to find in current working dir if not supplied.")
@click.option('--verbose', '-v', is_flag=True, help="Verbose mode.")
def cli(fs: str, generate_files: bool, do_delete: bool, config: str, verbose: bool) -> None:
    if generate_files:
        # Only import if actually necessary as the file is quite bloated.
        from klean.helpers.mock_files import generate_mock_files
        return generate_mock_files()

    config_path = config if config else os.path.join(os.getcwd(), 'klean', 'config.toml')
    configuration: dict = toml.load(config_path)
    file_system: Filesystem = get_file_system(fs, configuration)

    kill_list: List[str] = file_system.store_files_in_buckets(file_system.files_per_db)
    if do_delete:
        file_system.delete_files(kill_list, verbose=verbose)
    else:
        print('\n run Klean with --do-delete or -del to delete the files, run with --verbose to see all filenames '
              'and whether they will be deleted.')

    if verbose:
        for filename in file_system.sorted_files:
            print(filename, filename in kill_list)