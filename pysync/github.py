# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import asyncio
import re
from pathlib import Path
from types import SimpleNamespace


async def async_run_command(command):
    """ Run an async command and return stdout and stderr. """
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    return stdout, stderr


async def async_git_pull(repo_path=None, git_dir=None, work_tree=None):
    """`git pull` on a directory, or git directory and work tree for bare
    repos."""
    if repo_path:
        command = ['git', '-C', fr'"{repo_path}"', 'pull']
        command = ' '.join(command)
    else:
        command = [
            'git',
            f'--git-dir="{git_dir}"',
            f'--work-tree="{work_tree}"',
            'pull',
        ]
        command = ' '.join(command)

    stdout, stderr = await async_run_command(command)

    return stdout, stderr


async def async_git_push(repo_path=None, git_dir=None, work_tree=None):
    """`git push` on a directory, or git directory and work tree for bare
    repos."""
    if repo_path:
        command = ['git', '-C', fr'"{repo_path}"', 'push']
        command = ' '.join(command)
    else:
        command = [
            'git',
            f'--git-dir="{git_dir}"',
            f'--work-tree="{work_tree}"',
            'push',
        ]
        command = ' '.join(command)

    stdout, stderr = await async_run_command(command)

    return stdout, stderr


async def async_git_status(repo_path=None, git_dir=None, work_tree=None):
    """`git status` on a directory, or git directory and work tree for bare
    repos."""

    if repo_path:
        command = ['git', '-C', fr'"{ repo_path }"', 'status',
                   '--porcelain=2', '-b']
        command = " ".join(command)
    else:
        command = [
            'git',
            f'--git-dir="{git_dir}"',
            f'--work-tree="{work_tree}"',
            'status',
            '--porcelain=2',
            '-b'
        ]
        command = ' '.join(command)
    stdout, stderr = await async_run_command(command)

    return stdout, stderr


async def chain(repo_path=None, git_dir=None, work_tree=None, name=None):
    """ Chain pull, status, and push (for bare repos). """

    if type(repo_path) != str:

        git_dir = repo_path['git_dir']
        work_tree = repo_path['work_tree']
        name = repo_path.get('name', None)
        repo_path = None

    if name:
        pass
    elif repo_path:
        name = Path(repo_path).name
    else:
        name = Path(git_dir).name

    results = dict(name=name, pull={}, status={}, push={})

    if not repo_path:  # Bare Repos
        # Can't check ahead-behind, so...
        stdout, stderr = await async_git_push(repo_path, git_dir, work_tree)
        results['push']['stdout'], results['push']['stderr'] = stdout, stderr
    stdout, stderr = await async_git_pull(repo_path, git_dir, work_tree)
    results['pull']['stdout'], results['pull']['stderr'] = stdout, stderr
    stdout, stderr = await async_git_status(repo_path, git_dir, work_tree)
    results['status']['stdout'], results['status']['stderr'] = stdout, stderr

    return results


async def group(repos: iter):
    """Main function, but async.
    Chain pulls and status checks to each repo/bare repo, then run them.
    """
    return await asyncio.gather(
        *repos
    )


def parse_git_status(stdout):

    lines = stdout.splitlines()
    repo = SimpleNamespace()

    branch_info = [i for i in lines if i.startswith('#')]
    modified = [i for i in lines if i.startswith('1')]
    renamed_or_copied = [i for i in lines if i.startswith('2')]
    untracked = [i for i in lines if i.startswith('?')]
    ignored = [i for i in lines if i.startswith('!')]

    # Branch
    oid_group = '# branch.oid (?P<oid>.*)'
    head_group = '# branch.head (?P<head>.*)'
    upstream_group = '# branch.upstream (?P<upstream>.*)'
    ahead_behind_group = '# branch.ab (?P<ahead>.*) (?P<behind>.*)'
    space = r'\s*'
    branch_re = re.compile(fr'({oid_group})?'
                           + fr'{space}'
                           + fr'({head_group})?'
                           + fr'{space}'
                           + fr'({upstream_group})?'
                           + fr'{space}'
                           + fr'({ahead_behind_group})?'
                           )

    branch_info = [i for i in lines if i.startswith('#')]
    branch_match = branch_re.match('\n'.join(branch_info))

    branch = SimpleNamespace(
        oid=branch_match.group('oid'),
        head=branch_match.group('head'),
        upstream=branch_match.group('upstream'),
        ahead=int(branch_match.group('ahead')
                  if branch_match.group('ahead')
                  else 0),
        behind=int(branch_match.group('behind')
                   if branch_match.group('behind')
                   else 0),
    )

    # Changed
    modified = [get_file_info(i.split(maxsplit=9)) for i in modified]

    # Renamed or Copied
    renamed_or_copied = [get_file_info(i.split(maxsplit=10))
                         for i in renamed_or_copied]

    # Untracked
    untracked = [i.split(maxsplit=1)[1]
                 for i in untracked]
    untracked = [SimpleNamespace(path=i, type='Untracked')
                 for i in untracked]

    # Ignored
    # Only if `--ignored=matching` is included
    ignored = [i.split(maxsplit=1)[1] for i in ignored]
    ignored = [SimpleNamespace(path=i, type='Ignored') for i in ignored]

    # All Files
    all_files = modified + renamed_or_copied + untracked + ignored
    # Resort by Type
    modified = [i for i in all_files if i.type[0] == 'M']
    renamed = [i for i in all_files if i.type[0] == 'R']
    deleted = [i for i in all_files if i.type[0] == 'D']
    untracked = [i for i in all_files if i.type[0] == 'U']
    ignored = [i for i in all_files if i.type[0] == 'I']

    repo.branch = branch
    repo.ahead = branch.ahead
    repo.behind = branch.behind
    repo.modified = modified
    repo.renamed = renamed
    repo.deleted = deleted
    repo.untracked = untracked
    repo.ignored = ignored
    repo.all_changed_files = all_files

    # Quickfix
    if repo.branch.oid:
        repo.online = True
    else:
        repo.online = False

    return repo


def get_file_info(raw):

    if raw[0] == '1':
        type_ = 'changed'
    else:
        type_ = 'renamed_or_copied'
    raw = raw[1:]  # Get rid of the type as the docs don't refer to it.

    if type_ == 'renamed_or_copied':
        path = raw[8]
        original_path = raw[9]
    else:
        path = raw[7]
        original_path = None

    staged = False
    subtype = raw[0][-1] if raw[0][-1] != '.' else raw[0][0]
    if raw[0][0] == '.':
        staged = False
        subtype = raw[0][-1]
    elif raw[0][-1] == '.':
        staged = True
        subtype = raw[0][0]
    if subtype == 'D':
        subtype = 'Deleted'
    elif subtype == 'M':
        subtype = 'Modified'
    elif subtype == 'R':
        subtype = 'Renamed'

    file = SimpleNamespace(
        path=path,
        staged=staged,
        original_path=original_path,
        type=subtype,
    )

    return file
