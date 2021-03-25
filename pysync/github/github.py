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

# # FIX
#
# - GitRepo.install() will install in your current location (cwd)
#
# # TODO
#
# - Add parsing for pull commands (GitRepo.parse_status may work for this)

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

from shutil import which
import subprocess
import re


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
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.run([
                    self.command,
                    '--version'
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                startupinfo=startupinfo,
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
import sys
from types import SimpleNamespace
if sys.platform == 'win32':
    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    startup_info = None


class GitRepo(Package):

    command = 'git'
    install_command = 'clone'
    update_command = 'pull'
    status_command = 'status'

    def __init__(self,
                 name=None, path=None, repo=None, version=None,
                 dependencies=()
                 ):
        
        self.dependencies = dependencies + ('git',)
        self.repo = repo
        self.path = path
        self.version = version
        self.name = name

    def __repr__(self):

        class_name = self.__class__.__name__
        arguments = ", ".join([i for i in dir(self) if not i.startswith("__")])

        return f'{class_name}({arguments})'

    def install(self, path=None):
        
        if not path:
            path = self.path
        
        command = [
            self.command,
            self.install_command,
            path
        ]
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()
        
        print(stdout)
        print(stderr)

    def update(self):
        
        command = [
            self.command,
            '-C',
            self.path,
            self.update_command,
        ]
        
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()
        
        if stderr:
            print(stderr)
        
    def pull(self):
        self.update()
    
    @property
    def status(self):
        
        command = [self.command, '-C', self.path, self.status_command]
        
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startup_info,
        )
        stdout = process.stdout.decode()
        stderr = process.stderr.decode()
        
        return self.parse_status(stdout)
        
    @property
    def installed(self):
        pass
    
    @staticmethod
    def parse_status(stdout):
        
        if not stdout:
            return
        
        # Lines to ignore
        re_ignore = [
            'nothing to commit.*',
            'No commits yet',
            '.*use "git add <file>..." to include in what will be committed.*'
        ]

        # Branch
        re_branch = re.compile(r'On branch (\w+)')
        branch = re_branch.search(stdout).group(1)

        # Modified
        re_modified = re.compile(r'modified:\s*(.+)')
        modified = re_modified.findall(stdout)

        # Untracked
        re_untracked = re.compile('\s*Untracked files:\n.*?\n(.*)\n\s*\n',
                   flags=re.IGNORECASE | re.DOTALL)
        untracked = re_untracked.findall(stdout)
        untracked = list(map(str.strip, ''.join(untracked).splitlines()))

        # Stage
        # New Files
        re_new = re.compile(r'new file:\s*(.+)')
        new = re_new.findall(stdout)
        # Changes (staged files)
        re_all_changes = re.compile(re_new)
        re_changes = re.compile(r'Changes to be committed:\s*\(use "git rm --cached <file>..." to unstage\)'
                                + '\s*(.*?)\n\s*\n',
                               flags=re.DOTALL)
        changes = re_changes.findall(stdout)
        changes = list(map(lambda x: ''.join([i for i in x if i]), map(re_all_changes.split, map(str.strip, ''.join(changes).splitlines()))))
        
        # Branch, Modified, Untracked, (New, Changes)
        #new=new, - Took out since it's not really applicable
        result = SimpleNamespace(
            branch=branch,
            modified=modified,
            untracked=untracked,
            changes=changes,
        )
        return result


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
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.run([
                    self.command,
                    '--version'
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                startupinfo=startupinfo,
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
    repo_path = Path.home() / 'git_test'

    print(repo_path)
    assert repo_path.exists()

if __name__ == '__main__':
    repo = GitRepo(path=repo_path)

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

# # Notes
#
# Still very broken. REALLY doesn't like not having a valid repo, but that shouldn't matter if I'm trying to init one.
#
# What this should _really_ have is more validation and better error outputs, like "Not a valid GitHub repository. Please initialize first."
