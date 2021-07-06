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
    def load(cls, path: str):
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
        object_path = os.path.join(self.gitdir, 'objects', sha[0:2], sha[2:])
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
            if size != (len(raw) - y - 1):
                raise Exception(f'Malformed object {sha}: bad length')

            if   object_type == b'commit': c = GitCommit
            elif object_type == b'tree'  : c = GitTree
            elif object_type == b'tag'   : c = GitTag
            elif object_type == b'blob'  : c = GitBlob
            else: raise Exception(f"Unknown git object. type={object_type.decode('ascii')}, sha={sha}")

            return c(raw[y+1:])


class GitObject(ABC):

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes):
        pass

@dataclass(frozen=True)
class GitBlob(GitObject):
    blobdata: bytes = None

    def serialize(self) -> bytes:
        return self.blobdata

    @classmethod
    def deserialize(cls, data):
        print('blob object')
        cls(data)

class GitCommit(GitObject):

    def serialize(self) -> bytes:
        pass

    @classmethod
    def deserialize(cls, data: bytes):
        print('deserialize commit')
        cls()


class GitTree(GitObject):

    def serialize(self) -> bytes:
        pass


class GitTag(GitObject):

    def serialize(self) -> bytes:
        pass
