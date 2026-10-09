"""One read-only same75f parent stack observation, private only; no stop/deploy/start."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import pathlib,subprocess,hashlib,json,os,time
os.umask(0o077);assert os.geteuid()==0
def state():return dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show','schubert-nk-morning-controller.service','--property=MainPID,InvocationID,ExecMainStartTimestampMonotonic,ActiveState,SubState'],text=True).splitlines())
before=state();assert before['MainPID']=='3701511'and before['InvocationID']=='75f48ce36cd740e98a801eede7fdbb7f'and before['ExecMainStartTimestampMonotonic']=='185542282251'and before['ActiveState']=='activating'
p=pathlib.Path('/proc/3701511');argv=(p/'cmdline').read_bytes();assert hashlib.sha256(argv).hexdigest()=='868a34629788c1c3958e6f8fa6e46024efe30e89ae4ae89616f905e144fa7542'and int((p/'stat').read_text().rpartition(')')[2].split()[19])==18554228
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg888-live-diagnostic-v1');assert not os.path.lexists(save);save.mkdir(mode=0o700)
started=time.monotonic();r=subprocess.run(['/opt/jdk-25.0.4/bin/jcmd','3701511','Thread.print','-l'],capture_output=True,timeout=20)
for name,raw in [('stack.private.log',r.stdout),('error.private.log',r.stderr)]:
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
assert r.returncode==0 and before==state()and time.monotonic_ns()//1000<187342282251
main=r.stdout.decode('utf-8').split('"main"',1)[1].split('\n\n',1)[0];frames=[l.strip()for l in main.splitlines()if l.strip().startswith('at ')][:18]
print(json.dumps({'actualExit':0,'elapsedSeconds':time.monotonic()-started,'parent':before,'stackSha256':hashlib.sha256(r.stdout).hexdigest(),'mainFrames':frames,'productionSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','operationAuthority':False,'genuineAccepted':False,'formalAccepted':False}))
'''
if __name__=='__main__':
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 base=W/'pg888-live-diagnostic-v1';assert not Path(str(base)+'.private.log').exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 r=subprocess.run(ssh,input=PAYLOAD.encode(),capture_output=True,timeout=30)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr)
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(r.returncode)
