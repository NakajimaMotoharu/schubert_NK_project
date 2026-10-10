"""One durable external start of canonical same-active resume after full proof."""
import ast
import hashlib
import inspect
import json
from pg1182_canonical_runtime_post import payload as previous
from pg1041_cold_policy_diagnostic import W, P
import pg1120_current_failed_capture as transport


def payload():
    saved = json.loads((W/'pg1182-canonical-runtime-post-v1.safe.json').read_bytes())
    stage = json.loads((W/'pg1183-stage-v1.safe.json').read_bytes())
    if saved['actualExit'] != 0 or saved['privateAfterSha256'] != 'd218c5e294937078d6535b1871552a2bac1f4a3a81c8a46f47f0f018b79b8550' or stage['actualExit'] != 0:
        raise ValueError('actual independent canonical proof and fresh observer required')
    bundle = P/'pg1183-observer-stage-v1'
    expected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in bundle.iterdir()}
    if set(expected) != {'pg1183_watch_parent.py', 'pg457_stable_actor.py', 'pg462_observer_identity.py'}:
        raise ValueError('fixed observer source closure refused')
    s = previous();node = [n for n in ast.parse(s).body if isinstance(n, ast.Try)][-1]
    s = '\n'.join(s.splitlines()[:node.lineno-1])
    s = s.replace('canonical-runtime-post-v1', 'canonical-resume-once-v1')
    s = 'WATCH_FILES='+repr(expected)+'\n'+s+'\n'+BODY
    ast.parse(s);return s


BODY = r'''
def watch():
 p=pathlib.Path('/proc/424273');require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==5109843)
 require(str((p/'exe').readlink())=='/usr/bin/python3.14'and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='5869c4d00b38e1b32631fdf171ccd920ef6e3b595db61144c15f4e762a8a510b')
 status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1183-observer-v1');require(md(root)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and {p.name for p in root.iterdir()}==set(WATCH_FILES))
 for name,digest in WATCH_FILES.items():
  f=root/name;require(md(f)[2:6]==[0,0,stat.S_IFREG|0o400,1]and hashlib.sha256(f.read_bytes()).hexdigest()==digest)
def persist(name,value):
 with(SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
result=None
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 watch();observed=post();require(observed==post());watch()
 SAVE.mkdir(mode=0o700);persist('before.private.json',observed)
 persist('external-start-guard.private.json',{'source':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','boot':BOOT,'sameRun':RUN,'sameCutoff':CUTOFF,'sameActivation':ACT,'beforeSha256':'d218c5e294937078d6535b1871552a2bac1f4a3a81c8a46f47f0f018b79b8550','originalBudgetSeconds':1800,'repeatForbidden':True,'attemptReserved':True})
 watch();require(observed==post())
 result=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
 parent=show('schubert-nk-morning-controller.service',{'InvocationID','MainPID','Job','ExecMainStartTimestampMonotonic','LoadState'})
 persist('external-start-issued.private.json',dict(parent,clientExit=result.returncode,clientSuccessIsNotParentSuccess=True))
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
require(result is not None)
print(json.dumps({'externalStartIssuedOnce':True,'sameActiveRunCutoffActivation':True,'originalBudgetSeconds':1800,'canonicalConfigurationWritesReload0':True,'clientSuccessIsNotParentSuccess':True,'newMetadataNormalClose':True,'formalAccepted':False}))
raise SystemExit(result.returncode)
'''


def main():
    if not (W/'pg1183-watch-v1.started').exists() or (W/'pg1183-watch-v1.exit').exists():
        raise ValueError('live fresh observer required')
    snapshot = W/'pg1183-parent-watch-v1.private.jsonl'
    if not snapshot.exists() or snapshot.stat().st_size == 0:raise ValueError('fresh first observation required')
    s = inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1', 'pg1184-canonical-resume-once-v1').replace('PG1120-current-failed-capture-v1', 'PG1184-canonical-resume-once-v1')
    env = dict(transport.__dict__);env['PAYLOAD'] = payload()
    exec(compile(s, '<one current canonical same-active resume>', 'exec'), env);return env['main']()


if __name__ == '__main__':raise SystemExit(main())
