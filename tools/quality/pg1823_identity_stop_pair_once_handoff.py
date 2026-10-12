"""SSC282 current initial-before pair: one queued same-gate recovery only."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1820_identity_stop_retained_diagnosis import owner
from pg1822_identity_stop_current_pair_proof import payload as proof_payload,Current
from pg1813_current_warning_pair_handoff import payload as previous_handoff,match_peer_history
from pg1793_warning_fresh_history_contract import match_parent_history
from pg1724_retained_host_gate import queued_gate

SLOT='pg1823-identity-stop-pair-once-handoff-v1'
PROOF_SHA='9b2f5c8fdd5ba3a868ad23055c78680b5bd66347b64b1ef26700dc50a982ee29'


def payload():
    tree=ast.parse(proof_payload())
    boundaries=[i for i,n in enumerate(tree.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bus'for t in n.targets)]
    prefix=tree.body[:boundaries[-1]]
    saves=[n for n in prefix if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)]
    saves[-1].value=ast.parse('BASE/'+repr(SLOT),mode='eval').body
    for n in prefix:
        if isinstance(n,ast.FunctionDef)and n.name=='owned_lock':
            a=[x for x in ast.walk(n)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='actual'for t in x.targets)]
            if len(a)!=1 or ast.unparse(a[0].value)!='recovery_actor()':raise ValueError('one current locking actor required')
            a[0].value=ast.Call(func=ast.Name(id='actor_for_locks',ctx=ast.Load()),args=[],keywords=[])
    old=ast.parse(previous_handoff());start=next(i for i,n in enumerate(old.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CHILD_REAPED'for t in n.targets))
    body=Current().visit(ast.Module(body=old.body[start:],type_ignores=[]));ast.fix_missing_locations(body)
    originals=[n for n in body.body if isinstance(n,ast.FunctionDef)and n.name=='original']
    if len(originals)!=1:raise ValueError('one exact full current guard required')
    originals[0].body.extend(ast.parse("require(hashlib.sha256((BASE/'pg1808-native-stop-v1/before.private.json').read_bytes()).hexdigest()==retained_proof['retainedBeforeSha256'])\nrequire({p.name for p in (BASE/'pg1808-native-stop-v1').iterdir()}=={'before.private.json','refs-prepare.private.log'})").body)
    ast.fix_missing_locations(body)
    ast.fix_missing_locations(ast.Module(body=prefix,type_ignores=[]))
    raw=ast.unparse(ast.Module(body=prefix,type_ignores=[]))+'\n'+inspect.getsource(match_parent_history)+'\n'+inspect.getsource(match_peer_history)+'\n'+ast.unparse(body)+'\n'
    raw=raw.replace('pg1813-current-warning-pair-once-handoff-v1',SLOT).replace('33d9262d4564192bd5045840ca5fd2ce2a5db8dde8a431f21784c2d72df4c813',PROOF_SHA)
    from pyflakes.api import check
    if check(raw,'<actual current481511 queued handoff>'):raise ValueError('all emitted globals required')
    compile(raw,'<actual fixed initial-before recovery>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean source required')
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']:
        value=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        if 'SSC282'not in value and 'SSC-282'not in value:raise ValueError('published fixed current contract required')
    proof=json.loads((W/'pg1822-identity-stop-current-pair-proof-v1/manifest.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['guest']['proofSha256']!=PROOF_SHA:raise ValueError('current complete independent proof required')
    os.umask(0o077);held=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw);completed=False
    def validate_owner(path):
        if path!=P/'current-management-critical.lock'or owner()!=held:raise ValueError('same retained gate required')
        return True
    with queued_gate(P/'current-management-critical.lock',validate_owner=validate_owner,require_completion=lambda:completed)as acquired:
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=240)
        completed=r.returncode==0
        if completed and not acquired.wait(30):raise ValueError('same gate normal old-wrapper handoff required')
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldRetainedHostOwner':held,'queuedSameHostGateAcquired':completed,'oldNormalCloseUnknown':True,'formalAccepted':False}
    if completed:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
