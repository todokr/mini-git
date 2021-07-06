import os
from models import GitRepository

def run(repo_path: str):
    repo = GitRepository.load(repo_path)
    repo.init_git_dir()
    abs_gitdir = os.path.abspath(repo.gitdir)
    print(f'Initialized empty Git repository in {abs_gitdir}')
