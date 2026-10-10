"""New-only private same-byte physical pin component; never service/startup proof."""
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1282_physical_pin_compile import TARGET,SOURCE,W,sha
from pg1257_fresh_independent_terminal_post import SSH

AGENT_SHA='fb5b0036a0899ea97edfa0fc2c7985b55f3f7c5695028163e5e60d4f3cf6075d'
BODY=r'''
import base64,hashlib,json,os,pathlib,stat,subprocess,datetime
os.umask(0o077)
def require(value):
 if not value:raise ValueError('physical pin component refused')
def metadata(st):return(st.st_dev,st.st_ino,st.st_uid,st.st_gid,st.st_mode,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6')
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1283-physical-pin-v1')
require(not os.path.lexists(base))
agent=pathlib.Path('/opt/pgpt-tools-pg390/jacoco-agent.jar')
def observe():
 facts=[]
 for p in [pathlib.Path('/opt'),agent.parent,agent]:
  st=p.lstat();require(st.st_uid==st.st_gid==0 and not os.listxattr(p))
  if p==agent:require(stat.S_ISREG(st.st_mode)and st.st_mode==0o100644 and st.st_nlink==1 and st.st_size==307843)
  else:require(stat.S_ISDIR(st.st_mode)and st.st_mode==0o40755)
  facts.append(metadata(st))
 raw=agent.read_bytes();require(len(raw)==307843 and hashlib.sha256(raw).hexdigest()==AGENT_SHA)
 require(metadata(agent.lstat())==facts[-1])
 return facts,hashlib.sha256(pathlib.Path('/proc/self/mountinfo').read_bytes()).hexdigest()
before=observe();require(not(os.statvfs('/opt').f_flag&os.ST_RDONLY))
require(os.statvfs(base.parent).f_bavail*os.statvfs(base.parent).f_frsize>=134217728)
base.mkdir(mode=0o700);tools=base/'tools';tools.mkdir(mode=0o700)
for name,body in FILES.items():
 p=tools/name;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 raw=base64.b64decode(body,validate=True);require(hashlib.sha256(raw).hexdigest()==HASHES[name])
 with p.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
cp=':'.join(map(str,[tools,tools/'protocol.jar',tools/'storage.jar',tools/'bootstrap.jar']))
java='/opt/jdk-25.0.4/bin/java';clazz='dev.codex.schubert.nk.bootstrap.Pg1282PhysicalPinProbe'
phases={};started=datetime.datetime.now(datetime.timezone.utc)
for mode,expected in [('RW',b'RW_PIN_REFUSED_FD_RETURNED\n'),('RO',b'RO_PIN_VERIFIED_FD_RETURNED\n')]:
 dest=base/(mode.lower()+'.exec');require(not os.path.lexists(dest))
 args=[java,'--enable-native-access=ALL-UNNAMED','-javaagent:'+str(agent)+'=destfile='+str(dest)+',append=false,dumponexit=true,output=file','-cp',cp,clazz,mode]
 if mode=='RO':
  # Read-only namespace is owned by this bounded test child only. No host/Unit mounts mutate.
  namespace="import os,subprocess,sys;subprocess.run(['/usr/bin/mount','--bind','/opt','/opt'],check=True);subprocess.run(['/usr/bin/mount','-o','remount,bind,ro','/opt'],check=True);assert os.statvfs('/opt').f_flag&os.ST_RDONLY;raise SystemExit(subprocess.run("+repr(args)+").returncode)"
  args=['/usr/bin/unshare','--mount','--propagation','private','/usr/bin/python3','-B','-c',namespace]
 r=subprocess.run(args,stdin=subprocess.DEVNULL,capture_output=True,timeout=60)
 with(base/(mode.lower()+'.private.log')).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(r.stdout+r.stderr);f.flush();os.fsync(f.fileno())
 phases[mode]={'actualExit':r.returncode,'literalOutputMatched':r.stdout==expected,'stderrEmpty':r.stderr==b'','privateLogSha256':hashlib.sha256(r.stdout+r.stderr).hexdigest()}
 require(r.returncode==0 and r.stdout==expected and not r.stderr)
 st=dest.lstat();require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)==(0,0,0o600,1)and 0<st.st_size<=1048576 and not os.listxattr(dest))
 phases[mode].update(execBytes=st.st_size,execSha256=hashlib.sha256(dest.read_bytes()).hexdigest())
 require(observe()==before)
for name,digest in HASHES.items():require(hashlib.sha256((tools/name).read_bytes()).hexdigest()==digest)
require(observe()==before)
safe={'actualExit':0,'run':'PG1283-physical-pin-v1','candidateSource':SOURCE,'installedSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','phases':phases,'agentBytes':307843,'agentSha256':AGENT_SHA,'sameByteFrozenJarAndProbeVerified':True,'physicalRootOwnerModeLinksAclInodeHashVerified':True,'mountNamespaceReturnedUnchanged':True,'retainedPinFdReturned':True,'componentOnly':True,'applicationRootUnitStartupAccepted':False,'candidateDeployed':False,'formalAccepted':False,'startedUTC':started.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with(base/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for p in [tools,base,base.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps(safe))
'''


def payload(manifest):
    if manifest['actualExit']!=0 or manifest['source']!=SOURCE:
        raise ValueError('qualified current component compiler required')
    expected={'protocol.jar','storage.jar','bootstrap.jar','Pg1282PhysicalPinProbe.java',
      'dev/codex/schubert/nk/bootstrap/Pg1282PhysicalPinProbe.class','compile.private.log'}
    if set(manifest['fileHashes'])!=expected:raise ValueError('closed probe file set required')
    files={}
    for name,digest in manifest['fileHashes'].items():
        p=TARGET/name
        if sha(p)!=digest:raise ValueError('immutable component hash refused')
        files[name]=base64.b64encode(p.read_bytes()).decode()
    code='FILES='+repr(files)+'\nHASHES='+repr(manifest['fileHashes'])+'\nSOURCE='+repr(SOURCE)+'\nAGENT_SHA='+repr(AGENT_SHA)+'\n'+BODY
    compile(code,'<actual bounded physical pin component>','exec')
    return code


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean operator required')
    if json.loads((W/'pg1281-current-readonly-v1.safe.json').read_bytes())['actualExit']!=0:
        raise ValueError('current ownership full guard required')
    manifest=json.loads((TARGET/'manifest.safe.json').read_bytes());code=payload(manifest)
    base=W/'pg1283-physical-pin-v1'
    if any(Path(str(base)+suffix).exists()for suffix in ['.safe.json','.private.log','.exit']):raise ValueError('new-only actual slot required')
    started=datetime.datetime.now(datetime.timezone.utc)
    result=subprocess.run(SSH,input=code.encode(),capture_output=True,timeout=150)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    safe={'actualExit':result.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':started.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(result.stderr).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe.update(json.loads(result.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode


if __name__=='__main__':raise SystemExit(main())
