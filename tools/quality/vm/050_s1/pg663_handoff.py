"""SSC232 exact import-before-Ref Java handoff; no business operation authority."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from pg661_current_baseline import source

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')

PRELUDE=r'''
import signal,time
PID=2141065;TICKS=11112630;ARGV='4406b878234be0e15d15334e7238c029f27ebd0e8a85a63624546608d67c6367'
def process_identity(v):
 return(type(v)is dict and set(v)=={'pid','ticks','parent','argv','uid','exe','children'}and type(v['pid'])is int and v['pid']==2141065 and type(v['ticks'])is int and v['ticks']==11112630 and type(v['parent'])is int and v['parent']==2141063 and v['argv']=='4406b878234be0e15d15334e7238c029f27ebd0e8a85a63624546608d67c6367'and v['uid']==['0']*4 and v['exe']=='/opt/jdk-25.0.4/bin/java'and type(v['children'])is set and not v['children'])
def owned(present):
 if present:
  p=pathlib.Path('/proc')/str(PID);s=(p/'stat').read_text().rpartition(')')[2].split()
  value={'pid':PID,'ticks':int(s[19]),'parent':int(s[1]),'argv':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'uid':(p/'status').read_text().split('Uid:')[1].splitlines()[0].split(),'exe':str((p/'exe').readlink()),'children':{int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}}
  require(process_identity(value));require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==TICKS)
  links={str(f.readlink())for f in(p/'fd').iterdir()}
 else:require(not pathlib.Path('/proc',str(PID)).exists())
 for name in('maintenance.lock','startup-admission.lock'):
  path=pathlib.Path('/run/schubert-nk')/name;m=metadata(path);require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(path))
  hits=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':')
    if tuple(int(x,16)for x in d[:2])+(int(d[2]),)==(os.major(m[0]),os.minor(m[0]),m[1]):hits.append(f)
  if present:require(str(path)in links and len(hits)==1 and hits[0][1:5]==['FLOCK','ADVISORY','WRITE',str(PID)])
  else:require(not hits)
 error=pathlib.Path('/var/lib/pgpt-s1-preservation/pg662-bootstrap-verify-v1');require({p.name for p in error.iterdir()}=={'refs-prepare.private.log'})
 raw=strict(error/'refs-prepare.private.log',0o600,1048576);require(hashlib.sha256(raw).hexdigest()=='c1935ed537f31f678be275164c100acc7db979986bf47cd0688d0ec363b0d761'and b"ModuleNotFoundError: No module named 'pg556_parent_receipt'"in raw)
 tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg662-bootstrap-tools-v1');require({p.name for p in tools.iterdir()}==set(PINS))
 for name,digest in PINS.items():
  path=tools/name;m=metadata(path);require(m[2:6]==[0,0,stat.S_IFREG|0o400,1]and not os.listxattr(path)and hashlib.sha256(strict(path,0o400,33554432)).hexdigest()==digest)
 require(all(not os.path.lexists('/etc/schubert-nk/credentials/'+n)for n in('bootstrap-admin-username','bootstrap-admin-password')))
 require(not os.path.lexists('/run/credentials/schubert-nk-bootstrap-admin.service'))
def persist(name,value):
 with(root/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''


def payload():
    env={'__file__':str(R/'pg661_current_baseline.py'),'__name__':'template'}
    exec(compile(source(),'<current whole20 template>','exec'),env)
    raw=env['PAYLOAD']
    raw=raw.replace("root=base/'pg661-completed-baseline-v1'", "root=base/('pg663-handoff-'+MODE+'-v1')")
    raw=raw.replace("for name in('maintenance.lock','startup-admission.lock'):", "for name in():")
    anchor="before=capture();require(before==capture());root.mkdir(mode=0o700)"
    replacement="""owned(True);before=capture();require(before==capture());owned(True)
 require(hashlib.sha256(strict(base/'pg661-completed-baseline-v1/before.private.json',0o600,67108864)).hexdigest()=='8963796af5d95b30f01169d79bed2d6055782988af497dd09903b8f73a8af4d8')
 require(before==json.loads(strict(base/'pg661-completed-baseline-v1/before.private.json',0o600,67108864)))
 root.mkdir(mode=0o700);persist('profile.private.json',{'pid':PID,'ticks':TICKS,'argv':ARGV,'toolPins':PINS,'baselineSha256':'8963796af5d95b30f01169d79bed2d6055782988af497dd09903b8f73a8af4d8'})
 if MODE=='execute':
  prior=base/'pg663-handoff-preflight-v1';require(strict(prior/'profile.private.json',0o600,1048576)==strict(root/'profile.private.json',0o600,1048576))
  require(json.loads(strict(prior/'before.private.json',0o600,67108864))==before)
  fd=os.pidfd_open(PID);owned(True);require(before==capture());owned(True)
  persist('term-reservation.private.json',{'pid':PID,'ticks':TICKS,'argv':ARGV,'repeatForbidden':True,'businessActions0':True,'oldCloseUNKNOWN':True})
  owned(True);signal.pidfd_send_signal(fd,signal.SIGTERM);os.close(fd)
  deadline=time.monotonic()+15
  while pathlib.Path('/proc',str(PID)).exists()and time.monotonic()<deadline:time.sleep(.05)
  owned(False);require(before==capture()and before==capture());owned(False)
  persist('after.private.json',before)
  persist('complete.private.json',{'ownedToolGone':True,'allRawUnchangedTwice':True,'allPeerAdvisoryFlock0':True,'oldCloseUNKNOWN':True,'businessActions0':True})
"""
    assert anchor in raw;raw=raw.replace(anchor,replacement)
    raw=raw.replace("'operationAuthority':False", "'operationAuthority':MODE=='execute','ownedToolTermOnly':True,'oldCloseUNKNOWN':True,'mode':MODE")
    raw=raw.replace("'all10KernelAndResources0':True", "'all10KernelAndDbResources0':True,'ownedToolFlockPresent':MODE=='preflight','allFlock0':MODE=='execute'")
    raw=raw.replace("def file(p):",PRELUDE+"\ndef file(p):")
    return raw


def main():
    os.umask(0o077);assert len(sys.argv)==2 and sys.argv[1]in('preflight','execute');mode=sys.argv[1]
    assert subprocess.check_output(['git','status','--porcelain'])==b''
    root=W/'pg662-bootstrap-tools-v1'
    names=['Pg662BootstrapExisting.class','Pg662BootstrapExisting$References.class','pg662_bootstrap_existing.py','pg662_parent_receipt.py','pg662_parent_join.py']
    pins={name:hashlib.sha256((root/name).read_bytes()).hexdigest()for name in names}
    pins.update({name:hashlib.sha256((R/name).read_bytes()).hexdigest()for name in('pg535_bootstrap_contract.py','pg536_bootstrap_execution_contract.py','pg529_dependency_graph.py','pg559_terminal_refs.py','pg457_stable_actor.py','pg570_directory_identity.py')})
    raw=payload();digest=hashlib.sha256(raw.encode()).hexdigest()
    slot=W/('pg663-handoff-'+mode+'-v1');assert not any(Path(str(slot)+'.'+s).exists()for s in('exit','private.log','safe.json'))
    if mode=='execute':
        prior=json.loads((W/'pg663-handoff-preflight-v1.safe.json').read_bytes());assert prior['actualExit']==0 and prior['payloadSha256']==digest and prior['toolPins']==pins
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=('MODE='+repr(mode)+'\nPINS='+repr(pins)+'\n'+raw).encode(),capture_output=True)
    with Path(str(slot)+'.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(slot)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n');f.flush();os.fsync(f.fileno())
    if result.returncode==0:
        safe=json.loads(result.stdout);safe.update(payloadSha256=digest,toolPins=pins,startedUTC=started,endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        with Path(str(slot)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        print(json.dumps(safe))
    else:print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(result.stderr).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
