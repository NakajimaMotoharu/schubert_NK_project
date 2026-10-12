"""Current fixed initial-before failure profile; all ownership freshly captured."""
import ast
import hashlib
import json
import os
import subprocess
from pg1812_current_warning_pair_proof import payload as previous_payload
from pg1820_identity_stop_retained_diagnosis import owner,W,SSH

SLOT='pg1822-identity-stop-current-pair-proof-v1'


class Current(ast.NodeTransformer):
    def visit_Constant(self,node):
        numbers={479190:481511,479219:481540,479188:481509,8906867:9066715,8907026:9066872}
        value=node.value
        if type(value)is int and value in numbers:return ast.copy_location(ast.Constant(numbers[value]),node)
        if type(value)is str:
            value=str(numbers[int(value)])if value.isdecimal()and int(value)in numbers else value
            value=value.replace('pg1800','pg1808').replace('Pg1800','Pg1808').replace('PG1800','PG1808')
            value=value.replace('/proc/479190','/proc/481511').replace('/proc/479219','/proc/481540')
            value=value.replace('43b9447f91fd401abfb93ab77ce8b874842d124f94ef49724a035fcc7a80757c','4c8b121fe3121b919520901340a61884a5b9152c4d01fe1d49a90964adb61af1')
            value=value.replace('pg1812-current-warning-pair-proof-v1',SLOT)
        if type(value)is bytes:
            value=value.replace(b'pg1800',b'pg1808').replace(b'Pg1800',b'Pg1808').replace(b'PG1800',b'PG1808')
            if value==b'PG1808_FRAME method=verify_pid1 line=20':value=b'PG1808_FRAME method=main line=111'
        return ast.copy_location(ast.Constant(value),node)


def payload():
    tree=Current().visit(ast.parse(previous_payload()))
    frozen=json.loads((W/'pg1815-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('actual immutable current ABI required')
    assignments=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FROZEN'for t in n.targets)]
    if len(assignments)!=1:raise ValueError('one complete closure required')
    assignments[0].value=ast.parse(repr(frozen['fileHashes']),mode='eval').body;ast.fix_missing_locations(tree)
    raw=ast.unparse(tree)+'\n'
    marker="require({p.name for p in failure.iterdir()} == {'refs-prepare.private.log'})"
    if raw.count(marker)!=1:raise ValueError('one fixed retained-before directory required')
    raw=raw.replace(marker,"require({p.name for p in failure.iterdir()} == {'refs-prepare.private.log','before.private.json'})\n    captured_before=(failure/'before.private.json').read_bytes();captured=json.loads(captured_before)\n    require(captured['units']==current['units']and captured['rows']==current['rows']and captured['pid1']==current['pid1']and captured['startup']==current['startup']and captured['originals']==current['durable']['originals']and captured['backup']==current['durable']['backup'])")
    raw=raw.replace("'source': SOURCE, 'frozenHashes': FROZEN","'source': SOURCE, 'frozenHashes': FROZEN, 'retainedBeforeSha256': hashlib.sha256(captured_before).hexdigest()")
    if '4148e3e8-f107-431a-ab27-d6e6d1f1772e'not in raw:raise ValueError('actual Root UUID required')
    from pyflakes.api import check
    if check(raw,'<actual current481511 pair before proof>'):raise ValueError('all emitted globals required')
    compile(raw,'<retained initial-before proof>','exec');return raw


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('same retained host owner/phase required')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
