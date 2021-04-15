# -*- coding: utf-8 -*-
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

from blessed import Terminal

term = Terminal()


def repo_output_handler(repo, tabs=1):

    results = []
    indent = '\t'
    repo_condition = 'green'
    for i in repo.modified:
        results.append(term.yellow(f'{tabs*indent}modified: {i.path}'))
        repo_condition = 'yellow'
    for i in repo.renamed:
        results.append(
            term.yellow(f'{tabs*indent}renamed: {i.path} {i.original_path}')
        )
        repo_condition = 'yellow'
    for i in repo.untracked:
        results.append(term.yellow(f'{tabs*indent}untracked: {i.path}'))
        repo_condition = 'yellow'
    for i in repo.deleted:
        results.append(term.red(f'{tabs*indent}deleted: {i.path}'))
        repo_condition = 'red'
    for i in repo.ignored:
        results.append(term.red(f'{tabs*indent}ignored: {i.path}'))

    if not repo.online:
        repo_condition = 'blue'

    try:
        header = f"{(tabs-1)*indent} {repo.name}{' ' + repo.branch.head if repo.branch.head else ''} {repo.ahead:+} {repo.behind:+} ~{len(repo.modified)} -{len(repo.deleted)}"
        header = [(tabs - 1) * indent, repo.name]
        if repo.branch.head:
            header.append(term.magenta(repo.branch.head))
        if repo.ahead:
            header.append(term.cyan(f'↑{repo.ahead}'))
        if repo.behind:
            header.append(term.cyan(f'↓{repo.ahead}'))
        if repo.modified:
            header.append(term.cyan(f'~{len(repo.modified)}'))
        if repo.deleted:
            header.append(term.cyan(f'-{len(repo.deleted)}'))
        if repo.untracked:
            header.append(term.cyan(f'…{len(repo.untracked)}'))
        header = ' '.join(header)
    except:  # For Bare Repos
        header = f"{(tabs-1)*indent} {repo.name} {len(repo.modified):+}"

    if repo_condition == 'green':
        results.insert(0, term.green(f"✓ {header}"))
    elif repo_condition == 'yellow':
        results.insert(0, term.yellow(f"⚠ {header}"))
    elif repo_condition == 'red':
        results.insert(0, term.red(f"! {header}"))
    elif repo_condition == 'blue':
        results.insert(0, term.blue(f"? {header}"))

    return '\n'.join(results)
