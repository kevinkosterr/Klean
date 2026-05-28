import typer

from typing import Annotated, List
from enum import Enum

from klean.config import get_config
from klean.plugins import discover_plugins

app = typer.Typer(name="klean", no_args_is_help=True)
plugins = discover_plugins()

FilesystemChoice = Enum(
    "FilesystemChoice",
    {name: name for name in sorted(plugins.keys())},
)

@app.command()
def main(
    fs: Annotated[
        FilesystemChoice,
        typer.Argument(
            help="The filesystem to use"
        ),
    ],
    dry_run: Annotated[
        bool, typer.Option(is_flag=True, help="Enable dry run")
    ] = True,
    verbose: Annotated[
        bool, typer.Option(is_flag=True, help="Enable verbose output")
    ] = False,
):
    configuration: dict = get_config()
    filesystem = plugins[fs](config=configuration)

    kill_list: List[str] = filesystem.create_kill_list(filesystem.filenames_per_database)
    if dry_run:
        for filename in filesystem.sorted_filenames:
            typer.echo(f"{filename}, delete: {filename in kill_list}")
    else:
        filesystem.delete_files(kill_list, verbose=verbose)


