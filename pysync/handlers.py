# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from blessed import Terminal


def repo_output_handler(repo, tabs=1):

    results = []
    indent = '\t'
    repo_condition = 'green'
    for i in repo.modified:
        results.append(term.yellow(f'{tabs*indent}modified: {i.path}'))
        repo_condition = 'yellow'
    for i in repo.renamed:
        results.append(term.yellow(f'{tabs*indent}renamed: {i.path} {i.original_path}'))
        repo_condition = 'yellow'
    for i in repo.untracked:
        results.append(term.yellow(f'{tabs*indent}untracked: {i.path}'))
        repo_condition = 'yellow'
    for i in repo.deleted:
        results.append(term.red(f'{tabs*indent}deleted: {i.path}'))
        repo_condition = 'red'
    for i in repo.ignored:
        results.append(term.red(f'{tabs*indent}ignored: {i.path}'))
        repo_condition = 'red'

    try:
        header = f"{(tabs-1)*indent} {repo.name} {repo.ahead:+} {repo.behind:+} {len(repo.modified):+}"
    except:  # For Bare Repos
        header = f"{(tabs-1)*indent} {repo.name} {len(repo.modified):+}"
    if repo_condition == 'green':
        results.insert(0, term.green(f"✓ {header}"))
    elif repo_condition == 'yellow':
        results.insert(0, term.yellow(f"⚠ {header}"))
    elif repo_condition == 'red':
        results.insert(0, term.red(f"! {header}"))

    return '\n'.join(results)


term = Terminal()
