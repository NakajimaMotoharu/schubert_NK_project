"""New-only typed binding; old1809 failure remains immutable."""
import ast
import hashlib
import json
import os
import subprocess
from pg1809_current_warning_pair_proof import payload as previous_payload
from pg1805_retained_stop_readonly_diagnosis import owner,SSH,W

SLOT='pg1810-typed-current-warning-pair-proof-v1'


class Typed(ast.NodeTransformer):
    def visit_Constant(self,node):
        mapping={'476085':'479188','476087':'479190','476116':'479219','8492401':'8906867','8492565':'8907026'}
        if type(node.value)is str:
            v=mapping.get(node.value,node.value).replace('pg1809-current-warning-pair-proof-v1',SLOT)
            return ast.copy_location(ast.Constant(v),node)
        if type(node.value)is bytes and node.value==b'PG1800_FRAME method=capture_data line=58':return ast.copy_location(ast.Constant(b'PG1800_FRAME method=verify_pid1 line=20'),node)
        return node


def payload():
    tree=Typed().visit(ast.parse(previous_payload()));ast.fix_missing_locations(tree)
    raw=ast.unparse(tree)+'\n'
    if '4148e3e8-f107-431a-ab27-d6e6d1f1772e'not in raw:raise ValueError('actual original must remain unchanged')
    from pyflakes.api import check
    if check(raw,'<typed current actual pair proof>'):raise ValueError('closed emitted globals required')
    return raw


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('retained owner/phase changed')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
