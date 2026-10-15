"""Strict stopped9ffdbbc3 preservation schema: three flat/categorized roots, no relative I/O."""
import re
import stat
from pathlib import PurePosixPath

COUNTS={'originals':112,'backup':47,'extraDurable.credentials':19,'extraDurable.oldProofs':51}


def preservation_trees(snapshot):
    if type(snapshot)is not dict or not {'originals','backup','extraDurable'}<=snapshot.keys():
        raise ValueError('all three explicit preservation fields required')
    extra=snapshot['extraDurable']
    if type(extra)is not dict or set(extra)!={'credentials','oldProofs'}:
        raise ValueError('exact credential/old-proof categories required')
    trees=[('originals',snapshot['originals']),('backup',snapshot['backup']),
           ('extraDurable.credentials',extra['credentials']),('extraDurable.oldProofs',extra['oldProofs'])]
    for name,tree in trees:
        if type(tree)is not dict or len(tree)!=COUNTS[name]:
            raise ValueError('complete fixed stopped-snapshot category required')
        for path,item in tree.items():
            if (type(path)is not str or not PurePosixPath(path).is_absolute()or '..'in PurePosixPath(path).parts
                    or str(PurePosixPath(path))!=path or type(item)is not dict or set(item)!={'metadata','sha256'}):
                raise ValueError('canonical absolute leaf path and exact metadata fields required')
            meta=item['metadata'];digest=item['sha256']
            if type(meta)is not list or len(meta)!=9 or any(type(n)is not int or n<0 for n in meta):
                raise ValueError('complete nine integer metadata values required')
            if stat.S_ISDIR(meta[4]):
                if digest is not None:raise ValueError('directory must have no file digest')
            elif stat.S_ISREG(meta[4]):
                if type(digest)is not str or re.fullmatch('[0-9a-f]{64}',digest)is None:
                    raise ValueError('full regular-file digest required')
            else:raise ValueError('no symlink/device/unknown preservation leaf')
    return trees
