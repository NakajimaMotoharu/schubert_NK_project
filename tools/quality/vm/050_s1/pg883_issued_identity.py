"""Independent issued client0/current same-parent authentication; wrapper8821 remains failed."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import pathlib,json,subprocess,os,hashlib,time,stat
os.umask(0o077);assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg882-ordinary-once-v1');fields='MainPID,ControlPID,InvocationID,Job,ExecMainStartTimestampMonotonic,ActiveState,SubState'
def show():return dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show','schubert-nk-morning-controller.service','--property='+fields],text=True,timeout=5).splitlines())
before=show();raw=(root/'external-start-issued.private.json').read_bytes();issued=json.loads(raw)
for k,v in {'MainPID':'3701511','InvocationID':'75f48ce36cd740e98a801eede7fdbb7f','Job':'195974','ExecMainStartTimestampMonotonic':'185542282251','clientExit':0,'ordinaryNoargs':True,'oldCompletedRunNotResumed':True}.items():assert type(issued[k])is type(v)and issued[k]==v
for k in ('MainPID','InvocationID','Job','ExecMainStartTimestampMonotonic'):assert before[k]==issued[k]
assert before['ControlPID']=='0' and before['ActiveState']=='activating'and before['SubState']=='start' and time.monotonic_ns()//1000<187342282251
p=pathlib.Path('/proc/3701511');argv=(p/'cmdline').read_bytes();assert argv.endswith(b'dev.codex.schubert.nk.batch.file.MorningProcessMain\0')and int((p/'stat').read_text().rpartition(')')[2].split()[19])==18554228
assert(p/'cgroup').read_text()=='0::/system.slice/schubert-nk-morning-controller.service\n'
release=pathlib.Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes();assert str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG862'and hashlib.sha256(manifest).hexdigest()=='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'and json.loads(manifest)['source']['commit']=='e01612fcd7f2752df5ae0836b78538fd5e87f120'
active=pathlib.Path('/var/lib/schubert-nk/maintenance/active').read_bytes();assert hashlib.sha256(active).hexdigest()=='ce2af02a68e7a6f701a664d887b4973e27181c7877a124c8dbc27bf89aa92c79'
assert active.decode('ascii').splitlines()==['NKACT1','93cb976e-c36c-47a3-b9e2-0ad28d2996de','2026-10-09T19:07:23.894279Z','0dfe0b7f-0e36-4b81-9086-500d896d1187']
assert before==show()
print(json.dumps({'actualExit':0,'productionSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','issuedClientExit':0,'issuedSha256':hashlib.sha256(raw).hexdigest(),'parent':before,'pidTicks':18554228,'argvSha256':hashlib.sha256(argv).hexdigest(),'activeSha256':hashlib.sha256(active).hexdigest(),'wrapper882ActualExit':1,'wrapperNormalInferred':False,'parentGenuineAccepted':False,'operationAuthority':False,'formalAccepted':False}))
'''
if __name__=='__main__':
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg882-ordinary-once-v1.exit').read_bytes()==b'1\n'
 base=W/'pg883-issued-identity-v1';assert not Path(str(base)+'.private.log').exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 started=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=PAYLOAD.encode(),capture_output=True,timeout=30)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(r.returncode)
