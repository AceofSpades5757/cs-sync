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

import re
import subprocess
from pathlib import Path
from types import SimpleNamespace


# repo.status -> Status object
# Status.        
#
#
#
#
# self.branch = branch
#         self.ahead = branch.ahead
#         self.behind = branch.behind
#         self.modified = modified
#         self.renamed = renamed
#         self.deleted = deleted
#         self.untracked = untracked
#         self.ignored = ignored
#         self.all_changed_files = all_files

class Repo:

    def __init__(self, path=None):

        self.path = Path(path)
        self.name = self.path.stem
        self.valid = True
        self.get_status()

    def get_status(self):

        options = ['--porcelain=2', '-b']
        command = ['git', '-C', self.path, 'status'] + options
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()

        if 'fatal: not a git repository (or any of the parent directories): .git' in stderr:
            self.valid = False
            return

        lines = stdout.splitlines()

        branch_info = [i for i in lines if i.startswith('#')]
        modified = [i for i in lines if i.startswith('1')]
        renamed_or_copied = [i for i in lines if i.startswith('2')]
        untracked = [i for i in lines if i.startswith('?')]
        ignored = [i for i in lines if i.startswith('!')]

        # Branch
        branch_re = re.compile(r"""# branch.oid (?P<oid>.*)\n# branch.head (?P<head>.*)\n# branch.upstream (?P<upstream>.*)\n# branch.ab (?P<ahead>.*) (?P<behind>.*)""")

        branch_info = [i for i in lines if i.startswith('#')]
        branch_match = branch_re.match('\n'.join(branch_info))
        branch = SimpleNamespace(
            oid=branch_match.group('oid'),
            head=branch_match.group('head'),
            upstream=branch_match.group('upstream'),
            ahead=int(branch_match.group('ahead')),
            behind=int(branch_match.group('behind')),
        )

        # Changed
        modified = [self.get_file_info(i.split(maxsplit=9)) for i in modified]

        # Renamed or Copied
        renamed_or_copied = [self.get_file_info(i.split(maxsplit=10)) for i in renamed_or_copied]

        # Untracked
        untracked = [i.split(maxsplit=1)[1] for i in untracked]
        untracked = [SimpleNamespace(path=i, type='Untracked') for i in untracked]

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

        self.branch = branch
        self.ahead = branch.ahead
        self.behind = branch.behind
        self.modified = modified
        self.renamed = renamed
        self.deleted = deleted
        self.untracked = untracked
        self.ignored = ignored
        self.all_changed_files = all_files

    def get_file_info(self, raw):

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


class BareRepo:

    def __init__(self, git_dir, work_tree, name=None, *args, **kwargs):

        self.work_tree = Path(work_tree)
        self.git_dir = Path(git_dir)
        if name:
            self.name = name
        else:
            self.name = self.git_dir.stem
        self.valid = True
        self.get_status()

    def get_status(self):

        options = ['--porcelain=2', '-b']
        command = ['git', f'--git-dir={self.git_dir}', f'--work-tree={self.work_tree}', 'status'] + options
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()

        if 'fatal: not a git repository (or any of the parent directories): .git' in stderr:
            self.valid = False
            return

        lines = stdout.splitlines()

        branch_info = [i for i in lines if i.startswith('#')]
        modified = [i for i in lines if i.startswith('1')]
        renamed_or_copied = [i for i in lines if i.startswith('2')]
        untracked = [i for i in lines if i.startswith('?')]
        ignored = [i for i in lines if i.startswith('!')]

        # Branch
        branch_re = re.compile(r"""# branch.oid (?P<oid>.*)\n# branch.head (?P<head>.*)""")

        branch_info = [i for i in lines if i.startswith('#')]
        branch_match = branch_re.match('\n'.join(branch_info))
        branch = SimpleNamespace(
            oid=branch_match.group('oid'),
            head=branch_match.group('head'),
        )

        # Changed
        modified = [self.get_file_info(i.split(maxsplit=9)) for i in modified]

        # Renamed or Copied
        renamed_or_copied = [self.get_file_info(i.split(maxsplit=10)) for i in renamed_or_copied]

        # Untracked
        untracked = [i.split(maxsplit=1)[1] for i in untracked]
        untracked = [SimpleNamespace(path=i, type='Untracked') for i in untracked]

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

        self.branch = branch
        self.modified = modified
        self.renamed = renamed
        self.deleted = deleted
        self.untracked = untracked
        self.ignored = ignored
        self.all_changed_files = all_files

    def get_file_info(self, raw):

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
