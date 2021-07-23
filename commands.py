import os
import hashlib
import zlib

from models import GitRepository, GitObject

def run_init(repo_path: str):
    repo = GitRepository.load(repo_path)
    repo.init_git_dir()
    abs_gitdir = os.path.abspath(repo.gitdir)
    print(f'Initialized empty Git repository in {abs_gitdir}')


def run_cat_file(repo_path: str, sha: str) -> str:
    repo = GitRepository.load(repo_path)
    obj = repo.load_object(sha)
    return obj.serialize().decode('utf-8')

def run_hash_object(repo_path: str, object_type: str, write: bool, path: str):
    repo = GitRepository.load(repo_path)
    obj = repo.create_object_from_path(path, object_type)
    data = obj.serialize()
    payload = obj.fmt() + b' ' + str(len(data)).encode() + b'\x00' + data
    sha = hashlib.sha1(payload).hexdigest()
    if write:
        obj_dir = os.path.join(repo.gitdir, 'objects', sha[0:2])
        os.makedirs(obj_dir, exist_ok=True)
        obj_file = os.path.join(obj_dir, sha[2:])
        with open(obj_file, 'wb') as f:
            f.write(zlib.compress(payload))

    return sha

def run_log(repo_path: str, sha: str) -> str:
    repo = GitRepository.load(repo_path)
    commit_obj = repo.load_object(sha)
    assert(commit_obj.fmt() == b'commit')

    if not b'parent' in commit_obj.kvlm.keys():
        # Base case: the initial commit.
        return

    parents = commit_obj.kvlm[b'parent']
    message = commit_obj.kvlm[b''].decode('utf-8').replace('\n', ' ')
    committer = commit_obj.kvlm[b'committer'].decode('utf-8')
    print(f'{sha} {message} by {committer}')

    if type(parents) != list:
        parents = [ parents ]

    for p in parents:
        p = p.decode('ascii')
        run_log(repo_path, p)
