import subprocess
import asyncio
from pathlib import Path

from blessed import Terminal


term = Terminal()


async def async_run_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()
    return stdout, stderr


async def async_git_pull(repo_path=None, git_dir=None, work_tree=None):
    if repo_path:
        command = ['git', '-C', fr'"{ repo_path }"', 'pull']
        command = ' '.join(command)
    else:
        command = ['git', f'--git-dir="{repo_path}"',
                f'--work-tree="{work_tree}"', 'pull']
        command = ' '.join(command)
    stdout, stderr = await async_run_command(command)
    return stdout, stderr


async def async_git_status(repo_path=None, git_dir=None, work_tree=None):

    if repo_path:
        command = ['git', '-C', fr'"{ repo_path }"', 'status']
        command = ' '.join(command)
    else:
        command = ['git', f'--git-dir="{repo_path}"',
                f'--work-tree="{work_tree}"', 'status']
        command = ' '.join(command)
    stdout, stderr = await async_run_command(command)
    return stdout, stderr


# Add repos here!
repos = [
    Path.home() / 'vimfiles',
    Path.home() / 'wiki',
    Path.home() / 'Ublish',
]

dev_path = Path.home() / 'Development'
repos.extend([
    repo for repo in dev_path.glob('*')
    if dev_path.is_dir() and not dev_path.is_symlink()
    ])

# Add bare repos here!
dotfiles_git_directory = Path.home() / '.dotfiles'
dotfiles_work_dir = Path.home()

bare_repos = [(dotfiles_git_directory, dotfiles_work_dir)]


async def chain(repo_path=None, git_dir=None, work_tree=None):
    print(f'Starting {repo_path}')
    await async_git_pull(repo_path, git_dir, work_tree)
    await async_git_status(repo_path, git_dir, work_tree)
    print(f'Ending   {repo_path}')


async def async_main():
    await asyncio.gather(
        *([chain(repo) for repo in repos] +
            [chain(git_dir=bare_repo[0], work_tree=bare_repo[1])
                for bare_repo in bare_repos]
            )
    )


if __name__ == '__main__':

    start = __import__('time').perf_counter()
    print(f"""{__import__('pathlib').Path(__file__).name}
    started.""")

    # 14.58 seconds
    # main()
    # ~4 seconds
    asyncio.run(async_main())

    elapsed = __import__('time').perf_counter() - start
    print(f"""{__import__('pathlib').Path(__file__).name}
    executed in {elapsed:0.2f} seconds.""")
