import subprocess
import sys
from pathlib import Path
import yaml
from glob import glob
import functools
import operator
import asyncio
import time

import typer
from blessed import Terminal

from pysync.github import chain, group
from pysync.handlers import parse_repo


term = Terminal()
cli = typer.Typer()


# Config
config_file = Path.home() / '.pysync'


def expand_path(path):
    path = glob(str(Path(path).expanduser()))
    return path


def flatten_list(nested_list):
    return functools.reduce(operator.iconcat, nested_list, [])


def load_config() -> [list, list]:
    """ Get configuration from config file.

    Returns repo_paths and bare_repo_dicts.
    """
    if config_file.exists():
        with open(config_file, "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.Loader)
        repo_paths = flatten_list(
            [expand_path(i) for i in config.get('repo_paths', [])]
        )
        bare_repo_dicts = config.get('bare_repos', [])
        for i in bare_repo_dicts:
            i['git_dir'] = expand_path(i['git_dir'])[0]
            i['work_tree'] = expand_path(i['work_tree'])[0]
    else:
        repo_paths = []
        bare_repo_dicts = []
    return repo_paths, bare_repo_dicts


def measure_time_async(original_async_function):

    async def wrapper(*args, **kwargs):

        # Work Before
        start = __import__('time').perf_counter()

        # Run Async Function
        results = await original_async_function(*args, **kwargs)

        # Work After
        elapsed = __import__('time').perf_counter() - start
        print(term.red(f"Executed in {elapsed:0.2f} seconds."))

        # Return results
        return results

    return wrapper


def measure_time(original_async_function):

    def wrapper(*args, **kwargs):

        # Work Before
        start = __import__('time').perf_counter()

        # Run Async Function
        results = original_async_function(*args, **kwargs)

        # Work After
        elapsed = __import__('time').perf_counter() - start
        print(term.red(f"Executed in {elapsed:0.2f} seconds."))

        # Return results
        return results

    return wrapper


async def chain_handler(async_def, handler, *args, **kwargs):
    results = await async_def
    await handler(results, *args, **kwargs)
    return results


@cli.command()
def all(short: bool = typer.Option(False, "--short")):
    """ Git, AWS, System Settings (Windows Terminal), etc. """
    git(short=short)
    task()


@measure_time
@cli.command()
def git(short: bool = typer.Option(False, "--short")):
    """ Status, Pull, etc. all git repos. """

    repo_paths, bare_repo_dicts = load_config()
    repo_paths = [
        i
        for i in repo_paths
        if Path(i).is_dir() and '.git' in [j.name for j in Path(i).glob('*')]
    ]

    repos = repo_paths + bare_repo_dicts
    chains = [chain_handler(chain(r), parse_repo, short) for r in repos]
    tasks = group(chains)
    _ = asyncio.run(tasks)


@cli.command()
def task():
    """ Sync Taskwarrior with Taskserver. """

    command = ['task', 'sync']
    if sys.platform == 'win32':
        command = ['wsl'] + command
    subprocess.run(command)


if __name__ == '__main__':
    cli()
