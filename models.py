from abc import ABC, abstractmethod
import os
import configparser
import collections
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

            try:
                c = self._detect_cls(object_type)
            except Exception as e:
                raise Exception(f'{e}, sha:{sha}')

            return c.deserialize(raw[y+1:])

    def create_object_from_path(self, path: str, object_type: str):
        try:
            c = self._detect_cls(object_type.encode('ascii'))
        except Exception as e:
            raise Exception(f'{e}, path:{path}')
        target_path = os.path.join(self.worktree, path)
        return c.from_path(target_path)


    def _detect_cls(self, object_type: str):
        if   object_type == b'commit': c = GitCommit
        elif object_type == b'tree'  : c = GitTree
        elif object_type == b'tag'   : c = GitTag
        elif object_type == b'blob'  : c = GitBlob
        else: raise Exception(f"Unknown git object. type={object_type.decode('ascii')}")
        return c


class GitObject(ABC):
    @property
    def fmt(self):
        pass

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes):
        pass

    @classmethod
    @abstractmethod
    def from_path(cls, path: str):
        pass


@dataclass(frozen=True)
class GitBlob(GitObject):
    blobdata: bytes = None

    def fmt(self) -> bytes:
        return b'blob'

    def serialize(self) -> bytes:
        return self.blobdata

    @classmethod
    def deserialize(cls, data):
        return cls(data)


    @classmethod
    def from_path(cls, path):
        with open(path, 'rb') as f:
            blobdata = f.read()
            return cls(blobdata)

@dataclass(frozen=True)
class GitCommit(GitObject):
    kvlm: dict

    def fmt(self) -> bytes:
        return b'commit'

    def serialize(self) -> bytes:
        return kvlm_serialize(self.kvlm)

    @classmethod
    def deserialize(cls, data: bytes):
        kvlm = kvlm_parse(data)
        return cls(kvlm)

    @classmethod
    def from_path(cls, path):
        pass


class GitTree(GitObject):

    def fmt(self) -> bytes:
        return b'tree'

    def serialize(self) -> bytes:
        pass


class GitTag(GitObject):

    def serialize(self) -> bytes:
        pass

def kvlm_parse(raw, start=0, dct:dict=None) -> dict:
    if not dct:
        dct = collections.OrderedDict()
        # You CANNOT declare the argument as dct=OrderedDict() or all
        # call to the functions will endlessly grow the same dict.

    # We search for the next space and the next newline.
    spc = raw.find(b' ', start)
    nl = raw.find(b'\n', start)

    # If space appears before newline, we have a keyword.

    # Base case
    # =========
    # If newline appears first (or there's no space at all, in which
    # case find returns -1), we assume a blank line.  A blank line
    # means the remainder of the data is the message.
    if (spc < 0) or (nl < spc):
        assert(nl == start)
        dct[b''] = raw[start+1:]
        return dct

    # Recursive case
    # ==============
    # we read a key-value pair and recurse for the next.
    key = raw[start:spc]

    # Find the end of the value.  Continuation lines begin with a
    # space, so we loop until we find a "\n" not followed by a space.
    end = start
    while True:
        end = raw.find(b'\n', end+1)
        if raw[end+1] != ord(' '): break

    # Grab the value
    # Also, drop the leading space on continuation lines
    value = raw[spc+1:end].replace(b'\n ', b'\n')

    # Don't overwrite existing data contents
    if key in dct:
        if type(dct[key]) == list:
            dct[key].append(value)
        else:
            dct[key] = [ dct[key], value ]
    else:
        dct[key]=value

    return kvlm_parse(raw, start=end+1, dct=dct)

def kvlm_serialize(kvlm):
    ret = b''

    # Output fields
    for k in kvlm.keys():
        # Skip the message itself
        if k == b'': continue
        val = kvlm[k]
        # Normalize to a list
        if type(val) != list:
            val = [ val ]

        for v in val:
            ret += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'

    # Append message
    ret += b'\n' + kvlm[b'']

    return ret
