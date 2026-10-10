"""One durable normal noargs Root, legal new JST day, not old run resume."""
import ast
import datetime
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import pg1236_completed_runtime_retired_post as current

W=current.W;P=current.P
BEFORE='57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e'

def payload():
    bundle=P/'pg1237-observer-stage-v1';expected={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in bundle.iterdir()}
    if set(expected)!={'pg1237_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}:raise ValueError('exact current fresh observer closure required')
    s=current.payload();t=ast.parse(s);block=next(n for n in t.body if isinstance(n,ast.Try)and isinstance(n.body[0],ast.For))
    prefix=s[:sum(len(x)for x in s.splitlines(keepends=True)[:block.lineno-1])]
    snapshot=next(n for n in block.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    definition=ast.get_source_segment(s,snapshot);definition='\n'.join(x[1:]if x.startswith(' ')else x for x in definition.splitlines())
    s='WATCH_FILES='+repr(expected)+'\n'+prefix+'\n'+definition+'\n'+BODY
    compile(s,'<actual one normal new-day start>','exec');return s

BODY=r'''
raw=(base/'pg1238-fresh-day-ordinary-before-v1/before.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e');frozen=json.loads(raw)
require(frozen['current']==after and frozen['ordinaryNoargs']and frozen['existingSuccessfulInspectorStepsForDate']==0)
require(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()==frozen['newJstDate'])
SAVE=base/'pg1239-fresh-ordinary-once-v1';require(not os.path.lexists(SAVE))
def watch_identity():
 root=base/'pg1237-observer-v1';m=root.lstat();require(stat.S_ISDIR(m.st_mode)and(m.st_uid,m.st_gid,stat.S_IMODE(m.st_mode),m.st_nlink)==(0,0,0o700,2)and not os.listxattr(root));require(set(p.name for p in root.iterdir())==set(WATCH_FILES))
 for name,sha in WATCH_FILES.items():
  p=root/name;m=p.lstat();require(stat.S_ISREG(m.st_mode)and(m.st_uid,m.st_gid,stat.S_IMODE(m.st_mode),m.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==sha)
 argv=observer_argv()
 matches=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdecimal():continue
  try:cmd=(p/'cmdline').read_bytes()
  except (FileNotFoundError,ProcessLookupError,PermissionError):continue
  if cmd!=argv:continue
  status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
  require(str((p/'exe').readlink())=='/usr/bin/python3.14'and status['Uid'].split()==status['Gid'].split()==['0']*4)
  matches.append({'pid':int(p.name),'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(cmd).hexdigest()})
 require(len(matches)==1);return matches[0]
def observer_argv():
 return b'\0'.join([b'python3',b'-B',b'/var/lib/pgpt-s1-preservation/pg1237-observer-v1/pg1237_watch_parent.py',b'd5b00104280028d9ea81b44c1d1c805f3c2861ed',b'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',b'PG1068'])+b'\0'
def persist(name,v):
 with(SAVE/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(v,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 for p in [SAVE,SAVE.parent]:
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
result=None
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 watch=watch_identity();require(snapshot()==frozen['native']==snapshot()and watch==watch_identity())
 require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists()and not pathlib.Path(retirement.TARGET).exists())
 declaration=env['exec_record'](after['configuration']['schubert-nk-morning-controller.service']['ExecStart']);require(declaration is not None and declaration[1].endswith(' dev.codex.schubert.nk.batch.file.MorningProcessMain')and '--resume'not in declaration[1])
 SAVE.mkdir(mode=0o700);persist('before.private.json',frozen)
 persist('external-start-guard.private.json',{'productionSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','bomSha256':'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','beforeSha256':'57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e','ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'newJstDate':frozen['newJstDate'],'originalBudgetSeconds':1800,'watch':watch,'repeatForbidden':True,'attemptReserved':True})
 require(snapshot()==frozen['native']and watch==watch_identity())
 result=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],capture_output=True,timeout=15)
 parent=show('schubert-nk-morning-controller.service',{'InvocationID','MainPID','Job','ExecMainStartTimestampMonotonic','LoadState'})
 persist('external-start-issued.private.json',dict(parent,clientExit=result.returncode,clientSuccessIsNotParentSuccess=True,ordinaryNoargs=True))
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
require(result is not None)
print(json.dumps({'run':'PG1239-fresh-ordinary-once-v1','productionSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','externalStartIssuedOnce':True,'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'newJstDate':frozen['newJstDate'],'originalBudgetSeconds':1800,'parent':parent,'observer':watch,'clientExit':result.returncode,'clientSuccessIsNotParentSuccess':True,'newMetadataNormalClose':True,'formalAccepted':False}))
raise SystemExit(result.returncode)
'''

def main():
    if not(W/'pg1237-watch-v1.started').exists()or(W/'pg1237-watch-v1.exit').exists():raise ValueError('live fresh observer required')
    watch=W/'pg1237-parent-watch-v1.private.jsonl'
    if not watch.exists()or watch.stat().st_size==0:raise ValueError('actual first watch frame required')
    if json.loads((W/'pg1238-fresh-day-ordinary-before-v1.safe.json').read_bytes())['privateBeforeSha256']!=BEFORE:raise ValueError('qualified new day whole before required')
    entry=inspect.getsource(current.main).replace('pg1236-completed-runtime-retired-post-v1','pg1239-fresh-ordinary-once-v1')
    env=dict(current.__dict__);env['payload']=payload
    exec(compile(entry,'<one new day normal parent start transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
