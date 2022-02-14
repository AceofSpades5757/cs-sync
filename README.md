[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

# Descriptions

A custom syncing tool. Originally used to simply tasks such as checking on my local Git repositories and syncing to my Taskwarrior server. May someday add S3 support.

# Installation

PyPi - The Python Package Index

`pip install cs-sync`

## Current Support

* Git
  * **Works with bare repos**
* Taskwarrior

# Usage

Uses async operations, alongside package such as Click (what Typer is built upon) and blessed to create a pleasant experience checking on your local repos and syncing your tasks with your Taskwarrior server.

The default is to check your config file, located at `~/.cssync`, and load up your configuration details. If this is not the case, then it will use reasonable defaults for your local configuration.

## Git

`cs-sync git`
: Pulls on all repositories.
: Shows Repo `name` (actually folder name), branch, diff information, diff files (added, deleted, changes, etc.).

`--short`
: Won't show the repos that are up to date.

# Example .cssync file

```yaml
repo_paths:
  - ~/Development/*
  - ~/vimfiles
  - ~/wiki
  - ~/Work
  - ~/.git-hooks
bare_repos:
  - name: Dotfiles
    git_dir: ~/.dotfiles
    work_tree: ~/
```
