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

from pathlib import Path

#from github.github import GitRepo
# import github
from .github import GitRepo

# +
# Add repos here!
repos = [
    Path.home() / 'vimfiles',
    Path.home() / 'wiki',
    Path.home() / 'Ublish',
]

dev_path = Path.home() / 'Development'
repos.extend([repo for repo in dev_path.glob('*') if dev_path.is_dir() and not dev_path.is_symlink()])

# Add bare repos here!
dotfiles_git_directory = Path.home() / '.dotfiles'
dotfiles_work_dir = Path.home()

bare_repos = [(dotfiles_git_directory, dotfiles_work_dir)]

# +
repositories = []

for repo in repos:
    repositories.append(GitRepo(path=repo))
