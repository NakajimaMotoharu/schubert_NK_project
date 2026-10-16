"""Strict ten-field stop-after plus independently qualified native data; never coverage credit."""
import re
import stat
from pathlib import PurePosixPath

KEYS={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'}
PREFIX='/run/schubert-nk/pt-coverage/'


def require(value):
    if not value:raise ValueError('strict after10/native provenance required')


def expand(after,native,original,selected,excluded,count=40):
    require(type(after)is dict and set(after)==KEYS and type(native)is dict and type(original)is dict)
    require(type(selected)is list and type(excluded)is list and type(count)is int and count>0)
    def relative(name):
        require(type(name)is str and name and not name.startswith('/')and '\\'not in name and PurePosixPath(name).as_posix()==name and not any(x in {'','.','..'}for x in name.split('/')))
        return name
    expected={};directories={}
    for path,item in original.items():
        require(type(path)is str and(path==PREFIX[:-1]or path.startswith(PREFIX))and type(item)is dict and set(item)=={'metadata','sha256'})
        if item['sha256']is None:directories[path]=item
    for name in excluded:
        path=PREFIX+relative(name);require(path in original and path not in expected and original[path]['sha256']is not None);expected[path]=original[path]
    for item in selected:
        require(type(item)is dict and {'relative','metadata','sha256','bytes'}<=item.keys())
        path=PREFIX+relative(item['relative']);require(path not in expected)
        require(type(item['metadata'])is list and len(item['metadata'])==9)
        require(type(item['bytes'])is int and item['bytes']>0 and item['metadata'][6]==item['bytes'])
        expected[path]={'metadata':item['metadata'],'sha256':item['sha256']}
    require(len(expected)==count and set(native)==set(expected)|set(directories))
    for path,item in native.items():
        require(type(item)is dict and set(item)=={'metadata','sha256'})
        m=item['metadata'];require(type(m)is list and len(m)==9 and all(type(v)is int and v>=0 for v in m))
        if path in expected:
            require(stat.S_ISREG(m[4])and m[5]==1 and type(item['sha256'])is str and re.fullmatch('[a-f0-9]{64}',item['sha256'])is not None and item==expected[path])
        else:
            # Existing dirs may change size/mtime/ctime when new native leaves are
            # created. Exact inode/owner/mode/nlink and closed path set remain fixed.
            require(stat.S_ISDIR(m[4])and item['sha256']is None and m[:6]==directories[path]['metadata'][:6])
    return {**after,'native':native}
