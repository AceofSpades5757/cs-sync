import sys
import subprocess
from pathlib import Path
import platform
import concurrent.futures

import typer

# import pysync.github
# from pysync.github import repositories
# GitHub Repositories
# from pysync.config import repo_directories, bare_repos
from pysync.github import Repo, BareRepo
from pysync.handlers import repo_output_handler
    

cli = typer.Typer()


# Config
config_file = Path.home() / '.pysync'
if config_file.exists():
    exec(open(config_file).read())
    repos = [Repo(i) for i in repo_directories]
    repos = [r for r in repos if r.valid]
    bare_repos = [BareRepo(**i) for i in bare_repos]
    bare_repos = [i for i in bare_repos if i.valid]
else:
    repos = []
    bare_repos = []
repos = repos + bare_repos


if sys.platform == 'win32':

    py_version = sys.version_info
    py_version = f'{py_version.major}.{py_version.minor}'
    py_architecture = platform.architecture()[0][:2]

    python = f'py -{py_version}-{py_architecture}'.split()

elif sys.platform == 'linux':
    python = ['python3']


@cli.command()
def all():
    """ Git, AWS, System Settings (Windows Terminal), etc. """
    git()

@cli.command()
def git():
    """ Status, Pull, etc. all git repos. """
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(repo_output_handler, repo) for repo in repos]
        for future in concurrent.futures.as_completed(results):
            if future.result():
                print(future.result())

                
@cli.command()
def goodbye(name: str):
    """ Test. """
    typer.echo(f'Goodbye {name}!')


if __name__ == '__main__':
    cli()
