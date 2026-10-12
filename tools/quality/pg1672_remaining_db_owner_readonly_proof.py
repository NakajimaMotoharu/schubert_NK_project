"""BUG1152 current sole Java/DB owner after certified Ref reap; signals0."""
import inspect
import pg1664_current_unused_pair_readonly_proof as previous
from pg1673_sole_owner_contract import source

SLOT = 'pg1672-remaining-db-owner-proof-v1'

TAIL = r'''
private=base/'pg1667-unused-pair-owned-handoff-v1'
require({p.name for p in private.iterdir()}=={'old-proof.private.json','fresh-proof.private.json','fresh-complete.private','291242.term-once.private','291213.term-once.private'})
old=(private/'fresh-proof.private.json').read_bytes();require(hashlib.sha256(old).hexdigest()=='b84287218bb74e8ac546f3bbc763a5002fd2f0125e7242fbda9f3438b7283c2f')
old_pair=json.loads(old)['pair'];require(not pathlib.Path('/proc/291242').exists())
bus=dbus.SystemBus(private=True)
try:
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 require(not any(daemon.NameHasOwner(n)for n in old_pair['child']['busNames']))
finally:bus.close()
a=actor();require(a==actor()and len(a['fds'])==99)
old_fds=old_pair['parent']['fds'];require(set(old_fds)-set(a['fds'])=={'100','101'}and not set(a['fds'])-set(old_fds))
require({old_fds[n]['target']for n in ['100','101']}=={old_pair['child']['fds'][n]['target']for n in ['0','1']})
expected_actor={**old_pair['parent'],'fds':{k:v for k,v in old_fds.items()if k not in ['100','101']}}
import time
fresh_sole_parent(expected_actor,json.loads(json.dumps(a)),time.time_ns())
locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']];peer=same_peer();require(peer==same_peer()==old_pair['peer'])
save=base/'pg1672-remaining-db-owner-proof-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'actor':a,'locks':locks,'peer':peer,'native':native,'oldPair':old_pair,'toolHashes':TOOL_HASHES,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'onlyOwnedPeerAndAdvisory':True,'childReapedAndBusGone':True,'parentSignalNotSentSourceStackQualifiedOnHost':True,'candidateNotPlaced':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':291213,'ticks':5962776,'backendPid':291240,'fdCount':99,'childGone':True,'samePeer':True,'ownedLocks':2,'allOriginalValuesUnchanged':True,'candidateNotPlaced':True,'signals0':True,'formalAccepted':False}))
'''


def payload():
    raw = previous.payload()
    raw = raw[:raw.index("save=base/'pg1664-current-unused-pair-proof-v1'")]
    raw = raw.replace('require(children=={291242})', 'require(not children)')
    return source() + '\n' + raw + TAIL


def qualify_no_parent_signal():
    # Exact executed source places send strictly after reserve, whose nested
    # generation guard raised. A reservation is never treated as a signal receipt.
    from pg1446_current_cold_stage import W
    import ast
    import hashlib
    import json
    raw = (W / 'pg1667-unused-pair-owned-handoff-v1/payload.private.py').read_bytes()
    if hashlib.sha256(raw).hexdigest() != 'ffbf5516032bc0540d4b212ececee9ac54c8d7be1bba2afd9c1f676e68e636ea':
        raise ValueError('exact executed source required')
    nodes = ast.parse(raw).body
    function = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == 'terminate')
    calls = [n.value for n in function.body[2].body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)]
    if [n.func.id for n in calls if isinstance(n.func, ast.Name)][:2] != ['reserve', 'send']:
        raise ValueError('reserve must fail before send')
    error = (W / 'pg1667-unused-pair-owned-handoff-v1/stderr.private.log').read_text()
    if 'in reserve\n' not in error or 'in before_parent\n' not in error or 'in parent_after_ref\n' not in error or not error.rstrip().endswith('ValueError: no new/reused/changed remaining FD required'):
        raise ValueError('actual parent reserve guard refusal required')
    manifest = json.loads((W / 'pg1667-unused-pair-owned-handoff-v1/manifest.safe.json').read_bytes())
    if manifest['actualExit'] != 1 or len(manifest['stages']) != 1 or manifest['stages'][0]['signalsIssued'] != 0:
        raise ValueError('old actual refusal must remain separate')
    return True


def main():
    qualify_no_parent_signal()
    engine = previous.prior.prior
    ns = {**engine.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(engine.main), '<new remaining DB owner readonly transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
