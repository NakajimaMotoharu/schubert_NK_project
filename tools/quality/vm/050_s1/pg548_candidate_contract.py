"""Independent deployment artifact/frozen module identity contract; no filesystem writes."""
import hashlib
from pathlib import PurePosixPath
import zipfile

SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
OLD_SOURCE='a2e98ce9e96c42425921e3686e8ae7a94bff9e6c'
MODULES=('protocol','storage','bootstrap','api','web','batch')
CHANGED='batch:dev/codex/schubert/nk/batch/file/MorningCompletionEvidence.class'


def artifacts(value):
    if not isinstance(value,list)or len(value)!=187:
        raise ValueError('candidate artifact count')
    result={}
    for row in value:
        if not isinstance(row,dict)or not {'path','size','sha256'}<=set(row):
            raise ValueError('candidate artifact schema')
        name=row['path']
        if not isinstance(name,str)or not name or '\\'in name or PurePosixPath(name).is_absolute()or '..'in name.split('/')or '.'in name.split('/')or ''in name.split('/')or name in result:
            raise ValueError('candidate artifact path')
        if type(row['size'])is not int or row['size']<0 or not isinstance(row['sha256'],str)or len(row['sha256'])!=64 or set(row['sha256'])-set('0123456789abcdef'):
            raise ValueError('candidate artifact hash/size')
        result[name]=row
    return result


def class_inventory(path):
    with zipfile.ZipFile(path)as jar:
        names=jar.namelist()
        if len(names)!=len(set(names))or any(PurePosixPath(n).is_absolute()or '..'in n.split('/')for n in names):
            raise ValueError('candidate jar inventory')
        return {n:hashlib.sha256(jar.read(n)).hexdigest()for n in names if n.endswith('.class')}


def verify_delta(old,new):
    if set(old)!=set(MODULES)or set(new)!=set(MODULES):
        raise ValueError('candidate module inventory')
    changed=[];count=0
    for module in MODULES:
        if not isinstance(old[module],dict)or not isinstance(new[module],dict)or not old[module]or set(old[module])!=set(new[module]):
            raise ValueError('candidate class inventory')
        count+=len(new[module])
        changed.extend(module+':'+n for n in old[module]if old[module][n]!=new[module][n])
    if changed!=[CHANGED]:raise ValueError('candidate class delta')
    return count
