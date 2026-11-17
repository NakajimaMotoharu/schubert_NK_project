"""Single-attempt strict-pinned mini scratch transport; never retry a refused/unknown operation."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shlex
import sys

import pexpect

r=Path.cwd();os.umask(0o077);w=r.parent/'pgpt-runs/PG379';slot=w/'pg37320-p020-transport-v1'
sys.path.insert(0,str(r.parent/'PMO/hourly-monitor/haruka-transition-20261114'))
import remote_access
cfg=remote_access.config('haruka');account=cfg['users']['mini'];address=cfg['addr']
known=r.parent/'PMO/hourly-monitor/haruka_known_hosts'
remote='/home/mini/schubert-nk-pgpt/wbs66-p020-20261117-pg37322';package=w/'pg37318-p020-public-package-v1/public-package.tar'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
 with (slot/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def invoke(name,args,timeout):
 assert not (slot/(name+'.started.json')).exists()
 save(name+'.started.json',dict(startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),localPid=os.getpid(),operation=name,host='haruka',user='mini',remoteSlot=remote))
 child=pexpect.spawn(args[0],args[1:],encoding='utf-8',timeout=timeout,echo=False,maxread=65536);parts=[]
 try:
  prompt=child.expect([r'(?i)password:',pexpect.EOF,pexpect.TIMEOUT]);parts.append(child.before)
  if prompt==0:
   child.sendline(account);child.expect(pexpect.EOF,timeout=timeout);parts.append(child.before)
  elif prompt==2:raise TimeoutError('one attempt unknown; no automatic retry')
  child.close();code=child.exitstatus if child.exitstatus is not None else -int(child.signalstatus or 999)
 except BaseException:
  save(name+'.unknown.json',dict(state='UNKNOWN_NO_RETRY',childPid=child.pid,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()));raise
 raw=''.join(parts).replace(account,'[REDACTED]')
 save(name+'.terminal.json',dict(actualExit=code,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),output=raw,remoteSlot=remote))
 if code!=0:raise RuntimeError(name+' terminal nonzero; retained, no retry')
 print(json.dumps(dict(operation=name,actualExit=code)),flush=True);return raw
flags=['-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(known),'-o','ConnectTimeout=10','-o','NumberOfPasswordPrompts=1']
mode=sys.argv[1];assert mode in ['place','run','collect']
if mode=='place':
 assert not slot.exists();slot.mkdir(mode=0o700)
 admit="""from pathlib import Path
import os,json
p=Path('/home/mini/schubert-nk-pgpt/wbs66-p020-20261117-pg37322')
assert os.uname().nodename=='haruka' and os.getuid()==1000
assert p.parent.stat().st_uid==os.getuid() and not p.exists()
assert os.statvfs(p.parent).f_bavail*os.statvfs(p.parent).f_frsize>20*1024**3
assert os.statvfs('/tmp').f_bavail*os.statvfs('/tmp').f_frsize<20*1024**3
p.mkdir(mode=0o700)
print(json.dumps(dict(actualExit=0,hostname=os.uname().nodename,uid=os.getuid(),createdScratch=str(p),serviceDbVmNativeActions=0)))
"""
 invoke('new-scratch-admission',['ssh',*flags,'mini@'+address,'python3 -c '+shlex.quote(admit)],30)
 invoke('copy-public-package',['scp',*flags,str(package),'mini@'+address+':'+remote+'/public-package.tar'],90)
 unpack="""from pathlib import Path
import hashlib,json,tarfile,os
p=Path('/home/mini/schubert-nk-pgpt/wbs66-p020-20261117-pg37322');assert p.stat().st_uid==os.getuid()==1000
f=p/'public-package.tar';assert hashlib.sha256(f.read_bytes()).hexdigest()=='"""+sha(package)+"""'
assert not (p/'runner.py').exists() and not (p/'begin.json').exists()
with tarfile.open(f) as t:
 assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in t.getmembers())
 t.extractall(p,filter='data')
cfg=json.loads((p/'package.json').read_text());assert hashlib.sha256((p/'runner.py').read_bytes()).hexdigest()==cfg['runnerSha256']
print(json.dumps(dict(actualExit=0,packageSha256=hashlib.sha256(f.read_bytes()).hexdigest(),runnerSha256=cfg['runnerSha256'],jobStarted=False)))
"""
 invoke('extract-public-package',['ssh',*flags,'mini@'+address,'python3 -c '+shlex.quote(unpack)],30)
elif mode=='run':
 assert (slot/'extract-public-package.terminal.json').exists() and not (slot/'ordinary142.started.json').exists()
 invoke('ordinary142',['ssh',*flags,'mini@'+address,'cd '+shlex.quote(remote)+' && exec python3 runner.py'],600)
else:
 assert (slot/'ordinary142.terminal.json').exists() and not (slot/'collect.started.json').exists()
 target=w/'pg37322-p020-remote124-result.tar';assert not target.exists()
 invoke('collect',['scp',*flags,'mini@'+address+':'+remote+'/result.tar',str(target)],90)
 print(json.dumps(dict(resultSha256=sha(target),bytes=target.stat().st_size)),flush=True)
