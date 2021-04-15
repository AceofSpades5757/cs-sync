import subprocess
from pathlib import Path
import yaml
from glob import glob
import functools
import operator
import asyncio
import time

import typer
from blessed import Terminal

from pysync.github import async_git_pull, chain, group, parse_git_status
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
        repo_paths = flatten_list([expand_path(i) for i in config.get('repo_paths', [])])
        bare_repo_dicts = config.get('bare_repos', [])
        for i in bare_repo_dicts:
            i['git_dir'] = expand_path(i['git_dir'])[0]
            i['work_tree'] = expand_path(i['work_tree'])[0]
    else:
        repo_paths = []
        bare_repo_dicts = []
    return repo_paths, bare_repo_dicts


@cli.command()
def all():
    """ Git, AWS, System Settings (Windows Terminal), etc. """
    git()


@cli.command()
def git():
    
    """ Status, Pull, etc. all git repos. """
    
    repo_paths, bare_repo_dicts = load_config()
    repo_paths = [i for i in repo_paths if Path(i).is_dir() and '.git' in [j.name for j in Path(i).glob('*')]]
    
    # 3.58 seconds
    # Parsing: 4.04 seconds, 4.26 seconds, 3.89 seconds
    # Extend Parsing: 4.5 seconds
    # Filter repo_paths: 2.5 seconds, 3.06, 3.03
    repos = repo_paths + bare_repo_dicts
    chains = [chain(r) for r in repos]
    tasks = group(chains)
    output = asyncio.run(tasks)
    
    for o in output:
        status_stdout = o['status']['stdout']
        parsed = parse_git_status(status_stdout)
        parsed.name = o['name']
        print(repo_output_handler(parsed))
                
    elapsed = time.perf_counter() - start
    print(term.red(f"{len(repos)} executed in {elapsed:0.2f} seconds."))

if __name__ == '__main__':
    cli()