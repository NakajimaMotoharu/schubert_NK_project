"""SSC208 fixed guest owner handoff once. Capture private evidence; no business start."""
import hashlib,json,os,pathlib,subprocess
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes',
 '-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
raw=(R/'pg503_runtime_owned_handoff.py').read_bytes()
log=W/'pg503-runtime-handoff-v1.private.log';exit_file=W/'pg503-runtime-handoff-v1.exit';source=W/'pg503-runtime-handoff-v1.source.sha256'
assert not log.exists() and not exit_file.exists() and not source.exists()
subprocess.run(['python3','-B',str(R/'pg501_cold_handoff_test.py')],check=True)
with source.open('x') as f:f.write(hashlib.sha256(raw).hexdigest()+'\n')
with log.open('xb') as f:
 result=subprocess.run(ssh,input=raw,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with exit_file.open('x') as f:f.write(str(result.returncode)+'\n')
print(json.dumps({'id':'PG501-cold-handoff-v1','exitCode':result.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'oldCloseUNKNOWN':True}))
raise SystemExit(result.returncode)
