"""SSC285 separate full post: no lifecycle authority; original failure stays143."""
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg3510_signed_current_handoff as handoff
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate

SLOT = 'pg3512-signed-current-recovery-post-v1'


BODY = r'''
handoff=base/'pg3510-signed-current-handoff-v1'
require({p.name for p in handoff.iterdir()}=={'old-proof.private.json','fresh-proof.private.json','fresh-complete.private.json','410196.term-once.private.json','after.private.json','complete.private.json'})
def read(name):
 p=handoff/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata(p)==metadata_from_stat(s));return raw
def metadata_from_stat(s):return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
old_raw=read('old-proof.private.json');require(hashlib.sha256(old_raw).hexdigest()=='e9e071e218417501d6d64b41561cb45fc63dc34c73114362783c6a5a86177bc5')
fresh_raw=read('fresh-proof.private.json');require(hashlib.sha256(fresh_raw).hexdigest()==FRESH)
fresh=json.loads(fresh_raw);old=json.loads(old_raw)
require(json.loads(read('fresh-complete.private.json'))=={'freshProofSha256':FRESH,'independentFreshProofComplete':True,'signalsIssued':0,'oldCloseUnknown':True})
reservation=json.loads(read('410196.term-once.private.json'))
require(reservation=={'pid':410196,'ticks':8469964,'actor':canonical_actor(fresh['actor']),'signal':'TERM','replayAllowed':False,'freshProofSha256':FRESH})
after_raw=read('after.private.json');require(hashlib.sha256(after_raw).hexdigest()==AFTER)
require(json.loads(read('complete.private.json'))=={'ownedJavaGone':True,'oldCloseUnknown':True,'allOldResources0':True,'freshProofSha256':FRESH,'afterSha256':AFTER,'signalsIssued':1,'fullIndependentPostPending':True})
def no_old():
 require(not pathlib.Path('/proc/410196').exists()and not os.path.lexists(base/'pg3490-native-stop-v1'))
 for lock in fresh['locks']:
  p=pathlib.Path('/run/schubert-nk')/lock['name'];require(metadata(p)==lock['metadata'])
  s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}'
  require(not any(len(l.split())>=8 and l.split()[5]==key for l in pathlib.Path('/proc/locks').read_text().splitlines()))
def core(v):return {k:x for k,x in v.items()if k not in {'actor','locks','OFD43_128_same','OFD30_33_distinct'}}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in seal['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 no_old();a=ordinary_snapshot();b=ordinary_snapshot();no_old()
 require(a==b==json.loads(after_raw)==core(fresh)==core(old))
 save.mkdir(mode=0o700);encoded=json.dumps(a,sort_keys=True).encode()
 with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 for directory in [save,base]:
  fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'all24And32And18And187Unchanged':True,'fourOrdinaryOwnersAllTcpAndAllOriginalsUnchanged':True,'oldActorAndAllOwnedResourcesGone':True,'newTenRefsReturnedNormally':True,'signals0':True,'oldCloseUnknown':True,'fullRecoveryPost':True,'formalAccepted':False}))
'''


def payload():
    receipt=json.loads((W/handoff.SLOT/'manifest.safe.json').read_bytes())
    if receipt['actualExit']!=0 or len(receipt['stages'])!=2 or receipt['stages'][1]['signalsIssued']!=1:
        raise ValueError('one actual complete recovery required')
    stage=receipt['stages'][1]
    raw=handoff.proof.helpers(SLOT)+handoff.ordinary_helpers()
    raw+='\nFRESH='+repr(stage['freshProofSha256'])+'\nAFTER='+repr(stage['afterSha256'])+'\n'+BODY
    if check(raw,'<independent SSC285 full resource post>'):raise ValueError('complete post globals required')
    compile(raw,'<independent SSC285 post>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    raw=payload();(out/'payload.private.py').write_text(raw)
    if (W/'pg3494-stop-v1.exit').read_bytes()!=b'143\n' or os.path.exists('/proc/347505'):
        raise ValueError('original143 and old wrapper fully reaped required')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=150)
    (out/'stderr.private.log').write_bytes(r.stderr)
    v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'oldExit':143,'oldCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
