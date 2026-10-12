"""Fresh current479190/479219 full image; unchanged Root UUID and original.

Diagnosed fixed failed phase only; same retained host exclusion stays owned.
"""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1782_warning_live_peer_proof_direct import payload as old_payload
from pg1805_retained_stop_readonly_diagnosis import owner

SLOT='pg1809-current-warning-pair-proof-v1'


class Bound(ast.NodeTransformer):
    def visit_Constant(self,node):
        mapping={476087:479190,476116:479219,476085:479188,8492401:8906867,8492565:8907026}
        value=node.value
        if type(value)is int and value in mapping:return ast.copy_location(ast.Constant(mapping[value]),node)
        if type(value)is int and value==476114:return ast.copy_location(ast.Name(id='CURRENT_BACKEND',ctx=ast.Load()),node)
        if type(value)not in(str,bytes):return node
        if type(value)is bytes:
            value=value.replace(b'pg1772',b'pg1800').replace(b'Pg1772',b'Pg1800').replace(b'PG1772',b'PG1800')
            if value==b'476114\0':
                return ast.copy_location(ast.parse("str(CURRENT_BACKEND).encode()+b'\\0'",mode='eval').body,node)
        else:
            value=value.replace('pg1772','pg1800').replace('Pg1772','Pg1800').replace('PG1772','PG1800')
            value=value.replace('pg1782-warning-live-peer-readonly-v1',SLOT).replace('/proc/476087','/proc/479190').replace('/proc/476116','/proc/479219')
            value=value.replace('PG1800_FRAME method=capture_data line=58','PG1800_FRAME method=verify_pid1 line=20')
            if '476114'in value:
                chunks=value.split('476114');parts=[]
                for i,c in enumerate(chunks):
                    if i:parts.append(ast.FormattedValue(value=ast.Name(id='CURRENT_BACKEND',ctx=ast.Load()),conversion=-1))
                    parts.append(ast.Constant(c))
                return ast.copy_location(ast.JoinedStr(values=parts),node)
        return ast.copy_location(ast.Constant(value),node)


def payload():
    raw=old_payload();tree=Bound().visit(ast.parse(raw))
    frozen=json.loads((W/'pg1801-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('actual frozen ABI required')
    nodes=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FROZEN'for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one entire immutable closure required')
    nodes[0].value=ast.parse(repr(frozen['fileHashes']),mode='eval').body
    ast.fix_missing_locations(tree)
    prefix="""import hashlib,pathlib
current_child=(pathlib.Path('/proc/479219')/'cmdline').read_bytes()
assert hashlib.sha256(current_child).hexdigest()=='43b9447f91fd401abfb93ab77ce8b874842d124f94ef49724a035fcc7a80757c'
CURRENT_BACKEND=int(current_child.split(b'\\0')[-2])
assert CURRENT_BACKEND>1
"""
    raw=prefix+ast.unparse(tree)+'\n'
    if "4148e3e8-f107-431a-ab27-d6e6d1f1772e"not in raw or 'f1800e'in raw:raise ValueError('actual Root UUID must remain original')
    from pyflakes.api import check
    if check(raw,'<actual current479190 pair proof>'):raise ValueError('closed emitted globals required')
    compile(raw,'<actual sameSource pair proof>','exec');return raw


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    (out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('retained host gate/failed phase changed')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
