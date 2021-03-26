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

# # FIX
#
# - GitRepo.install() will install in your current location (cwd)
#
# # TODO
#
# - Add parsing for pull commands (GitRepo.parse_status may work for this)

from shutil import which
import subprocess
import re
from pathlib import Path
import sys
from types import SimpleNamespace

if sys.platform == 'win32':
    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    startup_info = None

readme=""" Describe a package

Features
--------
Install
Update/Upgrade
Dependencies
OS Support

Prototype
---------

Install Types
=============
Script - install_cygwin.py
Package Manager - PackageManager('apt')

Multiple - [PackageManager('apt'), 'install_cygwin.py', ...]
- Each one would be either dependent on platform or just a backup/failsafe.

Examples
========

ctags (universal)
>>> ctags = Package(
    description="ctags which can be Universal c-tags, etc.",
    install_method=
        command (sudo apt install {package}),
        install_script.py,
        PackageManager('apt'),
        {
            Windows: PackageManger('choco'),
            Ubuntu: PackageManger('apt'),
            Cygwin: PackageManger('apt-cyg'),
        }
    uninstall_method=See install_method,
        This will attempt to uninstall from the install_method if not provided.
    os=['Windows','Ubuntu','Cygwin'],
)
>>> ctags.install()
Installing for <Windows/Linux>...
>>> ctags.update()
Updateing <package>...
>>> ctags.uninstall()
Uninstalling <package>...

Test Example
============
>>> ctags = Package(
    description="CLI for tagging files.",
    install_method = dict(
        "Linux": PackageManager('apt'),
        "Windows": None,
    )
    os=['Linux'],
)
>>> ctags.install()
Installing ctags for Ubuntu...
"""


class Package:

    def __init__(self,
                 name, version=None,
                 dependencies=()):

        self.name = name
        self.version = version
        self.dependencies = dependencies

    def __str__(self):
        # Invalid syntax???
        if self.version:
            return f'Package("{self.name}", version="{self.version}")'
        else:
            return f'Package("{self.name}")'

    @property
    def installed(self):

        raise Exception('Unable to check installation')

    # raise Exception('This feature is not yet supported.')
    def install(self):
        pass
    def uninstall(self):
        pass
    def upgrade(self):
        pass


class CLI(Package):

    def __init__(self,
                 name, version=None,
                 command=None,
                 dependencies=()):

        if not command:
            self.command = name
        else:
            self.command = command

        if not version:
            p = subprocess.run([
                    self.command,
                    '--version'
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                startupinfo=startup_info,
            )
            output = p.stdout.decode()
            re_version = re.compile(r'[0-9.]+')
            version = max(re_version.findall(output)).strip('.')

            self.version = version

    def __repr__(self):

        class_name = self.__class__.__name__
        arguments = ", ".join([i for i in dir(self) if not i.startswith("__")])

        return f"""{class_name}(
    name            = {self.name},
    version         = {self.version},
    installed       = {self.installed},

    command         = {self.command},

    dependencies    = (
        {self.dependencies}
    )
)"""

    def __str__(self):

        return repr(self)

    @property
    def installed(self):

        return bool(which(self.command))


# +
#     def install(self, path=None):
        
#         if not path:
#             path = self.path
        
#         command = [
#             self.command,
#             self.install_command,
#             path
#         ]
#         process = subprocess.run(command,
#                                  stdout=subprocess.PIPE,
#                                  stderr=subprocess.PIPE,
#                                 )
#         stdout = process.stdout.decode()
#         stderr = process.stderr.decode()
        
#         print(stdout)
#         print(stderr)
# -

class PackageManager(Package):

    """
    TODO
    ----
    - [ ] Add support for snapshots.
    """

    # Global Package Manager installed packages
    packages = []

    def __init__(self,
                 name, version=None,

                 command=None,
                 install_command=None, uninstall_command=None,
                 update_command=None,

                 confirm_flag=None,

                 elevation=False,
                 dependencies=()
                 ):

        if not command:
            self.command = name
        else:
            self.command = command
        if not install_command:
            self.install_command = 'install'
        else:
            self.install_command = install_command
        if not uninstall_command:
            self.uninstall_command = 'uninstall'
        else:
            self.uninstall_command = uninstall_command
        if not update_command:
            self.update_command = 'upgrade'
        else:
            self.update_command = update_command

        if not confirm_flag:
            self.confirm_flag = '--yes'
        else:
            self.confirm_flag = confirm_flag
        self.elevation = elevation

        if not version:
            p = subprocess.run([
                    self.command,
                    '--version'
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                startupinfo=startup_info,
            )
            output = p.stdout.decode()
            re_version = re.compile(r'[0-9.]+')
            version = max(re_version.findall(output)).strip('.')

            self.version = version

        # Installed Packages for this package manager
        packages = []

        super().__init__(name, version)

    def __str__(self):
        return repr(self)
    def __repr__(self):

        class_name = self.__class__.__name__
        arguments = ", ".join([i for i in dir(self) if not i.startswith("__")])

        return f"""{class_name}(
    name            = {self.name},
    version         = {self.version},
    installed       = {self.installed},

    command         = {self.command},
    install         = {self.install_command},
    uninstall       = {self.uninstall_command},
    update          = {self.update_command},

    elevation       = {self.elevation},

    dependencies    = (
        {self.dependencies}
    )
)"""

    @property
    def installed(self):

        return bool(which(self.command))

    def install(self, packages, run=True, confirm=False):

        command = []
        if self.elevation:
            # raise Exception("Elevated priveldges are required.")
            """
            user = subprocess.run('whoami', stdout=subprocess.PIPE).stdout.decode().strip()
            command = [
                'runas',
                '/noprofile',
                f'/user:{user}',
                '""'
            ]
            """
            pass

        if type(packages)==str:
            if ' ' in packages.strip():
                packages = packages.strip().split()
                command = [
                    self.command,
                    self.install_command,
                    *packages
                ]
            else:
                command = [
                    self.command,
                    self.install_command,
                    packages
                ]
        else:
            command = [
                self.command,
                self.install_command,
                *packages
            ]

        if confirm:
            command.append(self.confirm_flag)

        if run:
            subprocess.run(command)
        else:
            return ' '.join(command)

    def uninstall(self, packages, run=True):

        if self.elevation:
            # raise Exception("Elevated priveldges are required.")
            pass

        command = []
        if type(packages)==str:
            if ' ' in packages.strip():
                packages = packages.strip().split()
                command = [
                    self.command,
                    self.uninstall_command,
                    *packages
                ]
            else:
                command = [
                    self.command,
                    self.uninstall_command,
                    packages
                ]
        else:
            command = [
                self.command,
                self.uninstall_command,
                *packages
            ]

        if run:
            subprocess.run(command)
        else:
            return ' '.join(command)


def installed_choco(check_package):
    p = subprocess.run([
            'choco',
            'list',
            '--local',
        ],
        stdout=subprocess.PIPE
    )

    output = p.stdout.decode()
    packages = output.splitlines()[2:-1]

    for name, version in [i.split() for i in packages]:
        package = Package(name, version)
        if package.name == check_package:
            return True

    return False


class GitManager(PackageManager):
    
    def install(self, uri, path=None, dry_run=False):
        
        if not path:
            path = str(Path())
        
        command = [
            self.command,
            self.install_command,
            uri,
            path,
        ]
        
        if dry_run:
            return command
        else:
            process = subprocess.run(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                    )
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()

            if stderr:
                print(stderr)
    
    def update(self, path=None, dry_run=False, *args, **kwargs):
        
        command = [self.command]
        command += ['-C', path] if path else []
        command += args if args else []
        for i, j in kwargs.items():
            command += [i, j]
        command += [self.update_command]
        
        if dry_run:
            return command
        else:
            process = subprocess.run(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                    )
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()

            if stderr:
                print(stderr)
                
    def config(self, dry_run=False, *args, **kwargs):
        command = [self.command, 'config', *args]
        for i, j in kwargs.items():
            command += [i, j]
        if dry_run:
            return command
        else:
            process = subprocess.run(
                command,
            )


git = GitManager(
    'git',
    command='git',
    install_command='clone',
    uninstall_command=None,
    update_command='pull',
)

if __name__ == '__main__':
    git.install('hey', dry_run=True)


class Repo(Package):

    #command = 'git'
    #install_command = 'clone'
    #update_command = 'pull'
    #status_command = 'status'
    package_manager = git

    def __init__(self,
                 path=None, name=None, version=None,
                 dependencies=()
                 ):
        
        self.dependencies = dependencies + ('git',)
        self.path = path
        self.version = version
        if not name:
            self.name = Path(self.path).stem
        else:
            self.name = name
        
        self.valid = True
        self.uri = self.get_uri()
        self.get_status()
        self.remote_status = self.check_remote()

    def __repr__(self):

        class_name = self.__class__.__name__
        arguments = ", ".join([i for i in dir(self) if not i.startswith("__")])

        return f'{class_name}({arguments})'

    def install(self, uri=None, path=None):
        
        if not path:
            path = self.path
        if not uri:
            uri = self.uri
        
        self.package_manager.install(path)

    def update(self):
        
        self.package_manager.update(path=self.path)
        
    def pull(self):
        
        self.update()
    
    @property
    def status(self):
        return self.get_status(dry_run=True)
        
    @property
    def installed(self):
        pass
    
    def get_uri(self):
        
        command = self.package_manager.config(dry_run=True, **{'-C': self.path, '--get': 'remote.origin.url'})
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()

        uri = stdout.strip()
        
        return uri
    
    def check_remote(self):
        
        command = [self.package_manager.command, '-C', self.path, 'ls-remote']
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()
        
        if 'fatal: Could not read from remote repository.' in stderr:
            return False
        else:
            return True
    
    def get_status(self, dry_run=False):

        options = ['--porcelain=2', '-b']
        command = [self.package_manager.command, '-C', self.path, 'status'] + options
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
        
        if dry_run:
            results = SimpleNamespace(
                branch=branch,
                ahead=branch.ahead,
                behind=branch.behind,
                modified=modified,
                renamed=renamed,
                deleted=deleted,
                untracked=untracked,
                ignored=ignored,
                all_changed_files=all_files,
            )
            return results

        else:
            self.branch = branch
            self.ahead = branch.ahead
            self.behind = branch.behind
            self.modified = modified
            self.renamed = renamed
            self.deleted = deleted
            self.untracked = untracked
            self.ignored = ignored
            self.all_changed_files = all_files
    
    @staticmethod
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


class BareRepo(Repo):

    def __init__(self, git_dir, work_tree, name=None, *args, **kwargs):

        self.work_tree = work_tree
        self.git_dir = git_dir
        if name:
            self.name = name
        else:
            self.name = Path(self.git_dir).stem
        self.valid = True
        self.remote_status = self.check_remote()
        self.get_status()

    def install(self, uri=None):
        pass
    
    def get_uri(self):
        
        command = self.package_manager.config(f'--git-dir={self.git_dir}', f'--work-tree={self.work_tree}', dry_run=True, **{'--get': 'remote.origin.url'})
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()

        uri = stdout.strip()
        
        return uri
    
    def update(self, **kwargs):
        
        self.package_manager.update(f'--git-dir={self.git_dir}', f'--work-tree={self.work_tree}')
        
    def check_remote(self):
        
        command = [self.package_manager.command, f'--git-dir={self.git_dir}', f'--work-tree={self.work_tree}', 'ls-remote']
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()
        
        if 'fatal: Could not read from remote repository.' in stderr:
            return False
        else:
            return True
    
    def get_status(self):

        options = ['--porcelain=2', '-b']
        command = [self.package_manager.command, f'--git-dir={self.git_dir}', f'--work-tree={self.work_tree}', 'status'] + options
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

# +
# if __name__ == '__main__':

    # Package Testing
    # git_package = Package(
        # 'git',
    # )
    # print(git_package)
    # print(git_package.installed)

    # CLI Testing
    # git_package = CLI(
        # 'git',
    # )
    # print(git_package)
    # print(git_package.installed)
    # print(git_package.version)
    # choco = PackageManager(
        # 'Chocolately',
        # command='choco',
        # install_command='install',
        # update_command='update',
        # # confirm_flag='--yes',
    # )
    # print(choco)
    # print(choco.installed)
    # print(choco.version)
    # choco.search()
    # print(choco.install('universal-ctags', run=False))
    # print(choco.install(['universal-ctags', 'test'], run=False))
    # print(choco.install('universal-ctags test', run=False))
    # print(choco.install('universal-ctags test', run=False, confirm=True))
    # print(choco.uninstall('universal-ctags test', run=False))

    # user = run('whoami', stdout=PIPE).stdout.decode()
    # print(p)
    # mycommand='hello'
    # run([
        # 'runas',
        # fr'/user:{user}',
        # 'powershell',
        # '-command',
        # 'echo Hello'
    # ])
        # '-command',
        # mycommand,
        # 'pause'
#     pass



# if __name__ == '__main__':

#     choco = PackageManager(
#         'Chocolately',
#         command='choco',
#         install_command='install',
#         update_command='update',
#         confirm_flag='--yes',
#     )
#     # print(choco)
#     packages = [
#         'universal-ctags',
#     ]
#     choco.install(packages)


# +
# Package
# PackageManager
# CLI
# GitRepo
# -

if __name__ == '__main__':
    from pathlib import Path
    repo_path = Path().absolute()

    print(repo_path)
    assert repo_path.exists()

if __name__ == '__main__':
    repo = Repo(path=repo_path)

    s = repo.status
    repo.pull()
    repo.update()
#     repo.install()
    print(s)

if __name__ == '__main__':
    repo_path = Path.home() / 'Development' / 'Finances'
    # print(repo_path)
    repo = GitRepo(path=repo_path)

    # print(repo_path.exists())
    assert repo_path.exists()

    s = repo.status
    print(s)
    repo.pull()
    repo.update()
#     repo.install()

if __name__ == '__main__':
    command = ['git', '-C', repo_path, 'pull']
    print(command)
    # print(' '.join(command))
    subprocess.run(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
