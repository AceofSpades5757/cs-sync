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

from pysync.github import chain, group, parse_git_status
from pysync.handlers import repo_output_handler


term = Terminal()
cli = typer.Typer()
start = time.perf_counter()


# Config
config_file = Path.home() / '.pysync'


def expand_path(path):
    path = glob(str(Path(path).expanduser()))
    return path


def flatten_list(nested_list):
    return functools.reduce(operator.iconcat, nested_list, [])


def load_config():
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


@cli.command()
def all(short: bool = typer.Option(False, "--short")):
    """ Git, AWS, System Settings (Windows Terminal), etc. """
    git(short=short)
    task()


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
    chains = [chain_2(chain(r), parse_repo, short) for r in repos]
    tasks = group(chains)
    output = asyncio.run(tasks)

    elapsed = time.perf_counter() - start
    print(term.red(f"{len(repos)} executed in {elapsed:0.2f} seconds."))


@cli.command()
def task():

    """ Sync Taskwarrior with Taskserver. """

    command = ['task', 'sync']
    if sys.platform == 'win32':
        command = ['wsl'] + command
    subprocess.run(command)


async def parse_repo(o, short=False):
    status_stdout = o['status']['stdout']
    parsed = parse_git_status(status_stdout)
    parsed.name = o['name']

    if short:
        # To tell if there's any changes that were made.
        any_changes = any(i for i in [
            parsed.ahead,
            parsed.behind,
            len(parsed.modified),
            len(parsed.renamed),
            len(parsed.deleted),
            len(parsed.untracked),
            len(parsed.ignored),
            ])
        if any_changes:
            print(repo_output_handler(parsed))
    else:
        print(repo_output_handler(parsed))


async def chain_2(async_def, handler, *args, **kwargs):
    results = await async_def
    await handler(results, *args, **kwargs)
    return results


if __name__ == '__main__':
    cli()
