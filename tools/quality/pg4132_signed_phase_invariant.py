"""Reuse qualified SSC244 held inode/ACL/hash inventory at every SSC287 action boundary."""
import ast
import hashlib
import inspect
import pg1026_cold_observation_contract as inventory


def source():
    tree=ast.parse(inspect.getsource(inventory))
    nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))
           or isinstance(n,ast.FunctionDef)and n.name in {'metadata','attributes','canonical_sum_bytes'}
           or isinstance(n,ast.ClassDef)and n.name=='HeldInventory']
    if sum(isinstance(n,ast.ClassDef)for n in nodes)!=1:raise ValueError('qualified inventory closure required')
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+WRAPPER
    compile(raw,'<signed inventory phase closure>','exec');return raw


WRAPPER=r'''
def verify(root,records,manifest_bytes,materials):
    if type(records)is not list or len(records)!=187 or type(manifest_bytes)is not bytes or type(materials)is not list or len(materials)!=2:
        raise ValueError('fixed signed phase inputs required')
    if any(type(row)is not dict or not {'path','size','sha256'}<=set(row)for row in records):
        raise ValueError('signed artifact fields required')
    all_records=[{k:row[k]for k in ['path','size','sha256']}for row in records]
    all_records.append({'path':'RELEASE-MANIFEST.json','size':len(manifest_bytes),'sha256':hashlib.sha256(manifest_bytes).hexdigest()})
    canonical=canonical_sum_bytes(records,hashlib.sha256(manifest_bytes).hexdigest())
    all_records.append({'path':'SHA256SUMS','size':len(canonical),'sha256':hashlib.sha256(canonical).hexdigest()})
    groups=[(root,all_records,False)]
    for value in materials:
        path=PurePosixPath(value['path'])
        if not path.is_absolute()or '..'in path.parts:raise ValueError('fixed material path required')
        groups.append((str(path.parent),[{'path':path.name,'size':value['size'],'sha256':value['sha256']}],True))
    for directory,entries,single in groups:
        held=HeldInventory(directory,entries,0)
        held.open_file()if single else held.open()
        try:
            # All ancestors and files are pinned by the existing O_NOFOLLOW real-FD contract.
            if any(acl for fd,parent,name,fixed,acl in held.held):raise ValueError('signed phase ACL refused')
            held.capture()
        finally:held.close()
    return True
'''


def digest():return hashlib.sha256(source().encode()).hexdigest()
