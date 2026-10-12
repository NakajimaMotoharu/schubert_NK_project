"""SSC281 single current pair recovery with queued unchanged host exclusion.

Current proof1812 only; old1802 never reissued or normalized.
"""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH,P
from pg1812_current_warning_pair_proof import payload as proof_payload
from pg1796_warning_fresh_pair_once_handoff import payload as historical_handoff
from pg1793_warning_fresh_history_contract import match_parent_history,same
from pg1809_current_warning_pair_proof import Bound
from pg1810_typed_current_warning_pair_proof import Typed
from pg1805_retained_stop_readonly_diagnosis import owner
from pg1724_retained_host_gate import queued_gate

SLOT='pg1813-current-warning-pair-once-handoff-v1'
PROOF_SHA='33d9262d4564192bd5045840ca5fd2ce2a5db8dde8a431f21784c2d72df4c813'


def match_peer_history(old,new,validate_peer):
    if type(old)is not dict or type(new)is not dict or set(old)!=set(new):raise ValueError('complete current peer image required')
    if not same(old['activity'],new['activity']):raise ValueError('fixed retained management activity required')
    validate_peer(new['allPeers'],1)
    before=[v for v in old['bindings']if v.get('role')=='schubert_batch']
    after=[v for v in new['bindings']if v.get('role')=='schubert_batch']
    if len(before)!=1 or not same(before,after)or new.get('liveDaemonPeersPreserved')is not True:raise ValueError('same management socket binding required')
    if len(new['bindings'])!=len(new['allPeers']):raise ValueError('every current ordinary peer socket required')
    return True


def payload():
    raw=proof_payload();tree=ast.parse(raw)
    boundaries=[i for i,n in enumerate(tree.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bus'for t in n.targets)]
    if not boundaries:raise ValueError('final actual metadata scope required')
    boundary=boundaries[-1]
    prefix=tree.body[:boundary]
    for node in prefix:
        if isinstance(node,ast.FunctionDef)and node.name=='owned_lock':
            assignments=[n for n in ast.walk(node)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='actual'for t in n.targets)]
            if len(assignments)!=1 or ast.unparse(assignments[0].value)!='recovery_actor()':raise ValueError('one current locking actor required')
            assignments[0].value=ast.Call(func=ast.Name(id='actor_for_locks',ctx=ast.Load()),args=[],keywords=[])
    old=ast.parse(historical_handoff())
    start=next(i for i,n in enumerate(old.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CHILD_REAPED'for t in n.targets))
    body=ast.Module(body=old.body[start:],type_ignores=[])
    body=Typed().visit(Bound().visit(body));ast.fix_missing_locations(body)
    for node in ast.walk(body):
        if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)and node.func.id=='match_peer_history':node.args.append(ast.Name(id='validate_peers',ctx=ast.Load()))
    raw=ast.unparse(ast.Module(body=prefix,type_ignores=[]))+'\n'+inspect.getsource(match_parent_history)+'\n'+inspect.getsource(match_peer_history)+'\n'+ast.unparse(body)+'\n'
    raw=raw.replace('pg1812-current-warning-pair-proof-v1',SLOT)
    raw=raw.replace('pg1796-warning-fresh-pair-once-handoff-v1',SLOT)
    raw=raw.replace('pg1794-warning-fresh-pair-readonly-v1/proof.private.json','pg1812-current-warning-pair-proof-v1/proof.private.json')
    raw=raw.replace('0351bb0dd4943d5ffb4dcbe4270333b32819ac175374a6eb99715785001c3400',PROOF_SHA)
    # Use existing approved pool bounds after management closes; every ordinary
    # peer is still independently matched to the same live service TCP owner.
    old_guard="require(len(peers) == 3 and sum((p['role'] == 'schubert_app' for p in peers)) == 2 and (sum((p['role'] == 'schubert_web_session' for p in peers)) == 1))"
    if raw.count(old_guard)!=1:raise ValueError('one ordinary post population predicate required')
    raw=raw.replace(old_guard,"require(set(p['role'] for p in peers)=={'schubert_app','schubert_web_session'} and 2<=sum(p['role']=='schubert_app'for p in peers)<=8 and 1<=sum(p['role']=='schubert_web_session'for p in peers)<=2 and len(set(p['pid']for p in peers))==len(peers) and len(set(p['port']for p in peers))==len(peers))")
    from pyflakes.api import check
    if check(raw,'<actual current pair queued handoff>'):raise ValueError('all current emitted globals required')
    compile(raw,'<same current pair once>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator source required')
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']:
        value=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        if 'SSC281'not in value and 'SSC-281'not in value:raise ValueError('published current recovery contract required')
    result=json.loads((W/'pg1812-current-warning-pair-proof-v1/manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['guest']['proofSha256']!=PROOF_SHA:raise ValueError('actual current independent full proof required')
    os.umask(0o077);held=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw);completed=False
    def validate_owner(path):
        if path!=P/'current-management-critical.lock'or owner()!=held:raise ValueError('exact retained same gate required')
        return True
    with queued_gate(P/'current-management-critical.lock',validate_owner=validate_owner,require_completion=lambda:completed)as acquired:
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=240)
        completed=r.returncode==0
        if completed and not acquired.wait(30):raise ValueError('normal recovered old wrapper did not release same gate')
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldRetainedHostOwner':held,'queuedSameHostGateAcquired':completed,'oldNormalCloseUnknown':True,'formalAccepted':False}
    if completed:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
