"""Dedicated pinned haruka read-only inventory. No application/job/test, uploads or admin commands."""
from pathlib import Path
import sys,os,json,hashlib,datetime,base64,shlex,pexpect
R=Path.cwd();P=R.parent/'PMO/hourly-monitor';sys.path.insert(0,str(P/'haruka-transition-20261114'))
from remote_access import config
os.umask(0o077)
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG30664-haruka-readonly-gate-eligibility-after-legitimate-repair-v3'
assert not out.exists();out.mkdir()
env=json.loads((P/'haruka-transition-20261114/HARUKA_EXECUTION_ENVIRONMENT.json').read_text())
assert env['hostName']=='haruka' and env['status']=='DIRECT_OS_BASELINE_READY'
kh=Path(env['knownHosts']);assert kh.is_file() and kh.stat().st_size>0
cfg=config('haruka');assert 'mini' in cfg['users']
code='''import os,json,pathlib,stat,hashlib,datetime
P=pathlib.Path;base=P('/home/mini/schubert-nk-pgpt');assert P('/etc/hostname').read_text().strip()=='haruka';assert os.getuid()!=0
def pathmeta(p):
 if not os.path.lexists(p):return dict(exists=False,path=str(p))
 s=os.lstat(p);return dict(exists=True,uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode)),symlink=stat.S_ISLNK(s.st_mode),directory=stat.S_ISDIR(s.st_mode),resolved=str(P(p).resolve()))
def fs(p):
 s=os.statvfs(p);return dict(availableBytes=s.f_bavail*s.f_frsize,totalBytes=s.f_blocks*s.f_frsize)
mem={l.split(':')[0]:int(l.split()[1]) for l in P('/proc/meminfo').read_text().splitlines() if l.split(':')[0] in ['MemTotal','MemAvailable','SwapTotal','SwapFree']}
jobs=[];unreadable=0
for p in P('/proc').iterdir():
 if not p.name.isdigit() or int(p.name)==os.getpid():continue
 try:
  if p.stat().st_uid!=os.getuid():continue
  cwd=(p/'cwd').resolve(strict=True)
  if cwd==base or base in cwd.parents:
   t=(p/'stat').read_text();jobs.append(dict(pid=int(p.name),name=(p/'comm').read_text().strip(),startTicks=int(t[t.rfind(')')+2:].split()[19])))
 except (FileNotFoundError,ProcessLookupError):pass
 except PermissionError:unreadable+=1
tools={}
for name,p in {'java':'/opt/schubert-nk-test-tools/jdk-25.0.4/bin/java','javac':'/opt/schubert-nk-test-tools/jdk-25.0.4/bin/javac','mvn':'/opt/schubert-nk-test-tools/maven/bin/mvn'}.items():
 q=P(p);tools[name]={**pathmeta(p),'readable':os.access(p,os.R_OK),'executable':os.access(p,os.X_OK),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
v=dict(atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),host='haruka',directOs=True,bootId=P('/proc/sys/kernel/random/boot_id').read_text().strip(),kernel=os.uname().release,uid=os.getuid(),gid=os.getgid(),selfPid=os.getpid(),selfStartTicks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),base=pathmeta(base),runs=pathmeta(base/'runs'),mavenRepository=pathmeta(base/'m2/repository'),disk=fs(base),tmpfs=fs('/dev/shm'),memoryKiB=mem,cpus=os.cpu_count(),tools=tools,ownedBaseProcesses=jobs,unreadableOwnProcessCwds=unreadable,filesCreated=0,testsExecuted=0,dbConnections=0,servicesChanged=0,signalsSent=0)
print('PGPT_READONLY_BEGIN');print(json.dumps(v));print('PGPT_READONLY_END')
'''
args=['-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(kh),'-o','GlobalKnownHostsFile=/dev/null','-o','UpdateHostKeys=no','-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','ControlMaster=no','-o','ConnectTimeout=12','-o','NumberOfPasswordPrompts=1','mini@'+cfg['addr'],'python3 -c '+shlex.quote('import base64;exec(base64.b64decode('+repr(base64.b64encode(code.encode()).decode())+'))')]
c=pexpect.spawn('/usr/bin/ssh',args,encoding='utf-8',echo=False,timeout=45);chunks=[];auth=0
while True:
 x=c.expect([r'(?i)password(?: for [^:\r\n]+)?:',pexpect.EOF,pexpect.TIMEOUT]);chunks.append(c.before)
 if x==0:
  auth+=1
  if auth>1:c.close(force=True);raise RuntimeError('Authentication unsuccessful; no retry')
  c.sendline(cfg['users']['mini'])
 elif x==1:break
 else:c.close(force=True);raise RuntimeError('Read-only connection timeout; do not infer remote job ownership')
c.close();text=''.join(chunks)
for secret in cfg['users'].values():
 if secret:text=text.replace(secret,'[REDACTED]')
terminal=dict(sshExit=c.exitstatus,sshSignal=c.signalstatus,authPrompts=auth,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputPublished=False)
(out/'terminal.json').write_text(json.dumps(terminal,indent=2)+'\n')
if c.exitstatus!=0:
 # Only allow public inventory traceback lines; raw SSH/auth text stays private in memory.
 lines=[line for line in text.splitlines() if line.startswith(('FileNotFoundError:','PermissionError:','IndexError:','AssertionError:','SyntaxError:'))]
 (out/'failure.json').write_text(json.dumps(dict(actualExit=c.exitstatus,publicInventoryErrors=lines,testsExecuted=0,newRuntimeJobs=0),indent=2)+'\n')
 raise SystemExit('Read-only inventory failed; terminal and bounded public error preserved, no runtime continuation')
v=json.loads(text.split('PGPT_READONLY_BEGIN',1)[1].split('PGPT_READONLY_END',1)[0])
assert v['host']=='haruka' and v['uid']==v['base'].get('uid')==v['runs'].get('uid') and not v['base']['symlink'] and not v['runs']['symlink']
high=v['disk']['availableBytes']>=20*1024**3;low=v['tmpfs']['availableBytes']<20*1024**3
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='2ebbdf391873a5be6247ea59cb9addffb886c591',strictPinnedPeer=True,knownHostsSha256=hashlib.sha256(kh.read_bytes()).hexdigest(),authSecretExported=False,sshAuthPrompts=auth,readOnlyInventory=v,highDiskPrecondition=high,lowTmpfsPrecondition=low,resourceEligibility=high and low and v['memoryKiB']['MemAvailable']>=3*1024**2 and not v['ownedBaseProcesses'] and v['unreadableOwnProcessCwds']==0 and v['mavenRepository'].get('exists') is True,eligibilityIsNotTestAdmission=True,newRemoteJobs=0,newRemoteTests=0,sourceUploaded=False,actualDbRootVmNativeKeyPermitDeploymentUnitOperations=0,aruOperations=0,oldOriginalJobOwnership='UNKNOWN_UNCHANGED',individualHoldsReleased=False,formalAcceptance=0)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['actualExit','strictPinnedPeer','highDiskPrecondition','lowTmpfsPrecondition','resourceEligibility','newRemoteJobs','newRemoteTests']}))
