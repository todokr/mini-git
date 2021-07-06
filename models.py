from abc import ABC, abstractmethod
import os
import configparser
from configparser import ConfigParser
from dataclasses import dataclass
import zlib

@dataclass(frozen=True)
class GitRepository:
    '''A git repository'''

    worktree: str
    gitdir: str

    @classmethod
    def create(cls, path: str):
        worktree = path
        gitdir = os.path.join(path, '.git')
        return cls(worktree, gitdir)

    def init_git_dir(self):
        if os.path.exists(self.worktree):
            if not os.path.isdir(self.worktree):
                raise Exception(f'{self.worktree} is not a directory')

            if os.path.exists(self.gitdir):
                raise Exception(f'{self.gitdir} is not empty')

            for gitdir_content in ['branches', 'objects', 'refs/tags', 'refs/heads']:
                path = os.path.join(self.gitdir, gitdir_content)
                os.makedirs(path)

            description_file = os.path.join(self.gitdir, 'description')
            with open(description_file, 'w') as f:
                f.write('A Git Repository')

            head_file = os.path.join(self.gitdir, 'HEAD')
            with open(head_file, 'w') as f:
                f.write('ref: refs/heads/master\n')

            config_file = os.path.join(self.gitdir, 'config')
            with open(config_file, 'w') as f:
                cp = ConfigParser()
                cp.add_section('core')
                cp.set('core', 'repositoryformatversion', '0')
                cp.set('core', 'filemode', 'false')
                cp.set('core', 'bare', 'false')
                cp.write(f)

        return self

    def load_object(self, sha: str):
        object_path = os.path.join(self.gitdir, 'object', sha[0:2], sha[2:])
        with open(object_path, 'rb') as f:
            raw = zlib.decompress(f.read())

            # object format exmaple
            # 00000000  63 6f 6d 6d 69 74 20 31  30 38 36 00 74 72 65 65  |commit 1086.tree|
            # 00000010  20 32 39 66 66 31 36 63  39 63 31 34 65 32 36 35  | 29ff16c9c14e265|
            # 00000020  32 62 32 32 66 38 62 37  38 62 62 30 38 61 35 61  |2b22f8b78bb08a5a|

            x = raw.find(b' ')
            object_type = raw[0:x]

            y = raw.find(b'\x00', x)
            size = int(raw[x:y].decode('ascii'))

class GitObject(ABC):

    @abstractmethod
    def serialize(self):
        pass

    @classmethod
    def deserialize(cls, data: bytes) -> GitObject:


class GitCommit(GitObject):

    def serialize(self):
        pass


class GitTree(GitObject):

    def serialize(self):
        pass


class GitTag(GitObject):

    def serialize(self):
        pass


class GitBlob(GitObject):

    def serialize(self):
        pass
