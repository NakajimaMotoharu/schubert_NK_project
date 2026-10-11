"""SSC243 one legal current new-day noargs Root, never replay/resume old Root.

Must have qualified actual before and a live source-fixed observer. Durable
new-only reservation precedes the only StartUnit; client0 is not parent success.
"""
import ast
import hashlib
import json
import os
import subprocess
from pg1453_current_cold_post import payload as post_payload
from pg1450_current_cold_retry import W
from pg1454_current_day_observer import namespace
from pg1446_current_cold_stage import P,SSH


def compose(before_sha,watch_files):
    if not isinstance(before_sha,str)or len(before_sha)!=64 or any(c not in '0123456789abcdef'for c in before_sha):raise ValueError('before SHA required')
    if not isinstance(watch_files,dict)or set(watch_files)!= {'pg1454_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}or any(not isinstance(v,str)or len(v)!=64 or any(c not in '0123456789abcdef'for c in v)for v in watch_files.values()):raise ValueError('watch closure required')
    raw=post_payload().split('bus=dbus.SystemBus',1)[0]
    marker="SAVE=BASE/'pg1453-current-cold-independent-post-v1';SAVE.mkdir(mode=0o700)"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"SAVE=BASE/'pg1456-current-day-once-v1';require(not os.path.lexists(SAVE))")
    raw+='\nBEFORE_SHA='+repr(before_sha)+'\nWATCH_FILES='+repr(watch_files)+'\n'+BODY
    ast.parse(raw);return raw


BODY=r'''
raw=(BASE/'pg1455-current-day-before-v1/before.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==BEFORE_SHA);frozen=json.loads(raw)
require(frozen['ordinaryNoargs'] and frozen['existingSuccessfulInspectorStepsForDate']==0)
require(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()==frozen['newJstDate'])
def watch_identity():
 root=BASE/'pg1454-observer-v1';require(metadata(root)[2:6]==[0,0,stat.S_IFDIR|0o700,2] and not os.listxattr(root) and set(os.listdir(root))==set(WATCH_FILES))
 for name,digest in WATCH_FILES.items():
  file=root/name;m=metadata(file);require(m[2:6]==[0,0,stat.S_IFREG|0o400,1] and hashlib.sha256(file.read_bytes()).hexdigest()==digest and metadata(file)==m)
 argv=b'\0'.join([b'python3',b'-B',str(root/'pg1454_watch_parent.py').encode(),SOURCE.encode(),BOM.encode(),b'PG1292'])+b'\0'
 matches=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdecimal():continue
  try:cmd=(p/'cmdline').read_bytes()
  except(FileNotFoundError,ProcessLookupError,PermissionError):continue
  if cmd!=argv:continue
  status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
  require(str((p/'exe').readlink())=='/usr/bin/python3.14' and status['Uid'].split()==status['Gid'].split()==['0']*4)
  matches.append({'pid':int(p.name),'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(cmd).hexdigest()})
 require(len(matches)==1);return matches[0]
def persist(name,value):
 with(SAVE/name).open('xb')as f:f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[];issued=False;result=None
try:
 for n in UNITS:manager.LoadUnit(n);manager.RefUnit(n);refs.append(n)
 first=snapshot();require(first==frozen['current'] and first==snapshot());require(runtime_check()==frozen['runtime'])
 watch=watch_identity();require(watch==watch_identity())
 decl=exec_record(first['configuration']['schubert-nk-morning-controller.service']['ExecStart'])
 require(decl is not None and decl[1].endswith(' dev.codex.schubert.nk.batch.file.MorningProcessMain') and '--resume'not in decl[1])
 require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg492-once-resume.conf').exists())
 require(min(os.statvfs(p).f_bavail*os.statvfs(p).f_frsize for p in[BASE,pathlib.Path('/srv/schubert-nk/backup')])>=805306368)
 SAVE.mkdir(mode=0o700);persist('before.private.json',frozen)
 persist('external-start-guard.private.json',{'source':SOURCE,'bomSha256':BOM,'boot':BOOT,'beforeSha256':BEFORE_SHA,'newJstDate':frozen['newJstDate'],'originalBudgetSeconds':1800,'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'watch':watch,'attemptReserved':True,'repeatForbidden':True,'operatorInvalidIssued':False})
 parentfd=os.open(SAVE.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(parentfd);os.close(parentfd)
 require(snapshot()==frozen['current'] and runtime_check()==frozen['runtime'] and watch_identity()==watch)
 issued=True
 result=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],capture_output=True,timeout=15)
 parent=show('schubert-nk-morning-controller.service')
 persist('external-start-issued.private.json',dict(parent,clientExit=result.returncode,clientSuccessIsNotParentSuccess=True))
finally:
 errors=[]
 for n in reversed(refs):
  try:manager.UnrefUnit(n)
  except Exception as e:errors.append(type(e).__name__)
 try:bus.close()
 except Exception as e:errors.append(type(e).__name__)
 require(not errors)
require(result is not None and issued)
print(json.dumps({'run':'PG1456-current-day-once-v1','source':SOURCE,'boot':BOOT,'externalStartIssuedOnce':True,'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'newJstDate':frozen['newJstDate'],'originalBudgetSeconds':1800,'clientExit':result.returncode,'clientSuccessIsNotParentSuccess':True,'parent':parent,'observer':watch,'metadataScopesClosedNormally':True,'formalAccepted':False},sort_keys=True))
raise SystemExit(result.returncode)
'''


def payload():
    v=json.loads((W/'pg1455-current-day-before-v1/manifest.safe.json').read_bytes());assert v['actualExit']==0
    bundle=P/'pg1454-observer-stage-v1';hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in bundle.iterdir()}
    actual={name:hashlib.sha256(raw.encode()).hexdigest()for name,raw in namespace()['files']().items()}
    assert hashes==actual
    return compose(v['guest']['privateBeforeSha256'],hashes)


def main():
    assert not subprocess.check_output(['git','status','--porcelain'])
    assert(W/'pg1454-watch-v1.started').exists()and not(W/'pg1454-watch-v1.exit').exists()
    assert(W/'pg1454-parent-watch-v1.private.jsonl').stat().st_size>0
    os.umask(0o077);out=W/'pg1456-current-day-once-v1';out.mkdir(mode=0o700)
    code=payload().encode()
    with(out/'payload.private.py').open('xb')as f:f.write(code);f.flush();os.fsync(f.fileno())
    with(out/'observer.private.log').open('xb')as f:r=subprocess.run(SSH+['sudo','-n','python3','-'],input=code,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(code).hexdigest(),'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True));return r.returncode


if __name__=='__main__':raise SystemExit(main())
