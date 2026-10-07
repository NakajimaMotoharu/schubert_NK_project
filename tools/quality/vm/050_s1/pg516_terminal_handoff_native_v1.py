"""SSC211 one fixed current owner handoff. No business stop/epoch action."""
import hashlib,json,os,pathlib,subprocess
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
subprocess.run(['python3','-B',str(R/'pg516_terminal_handoff_test.py')],check=True)
subprocess.run(['python3','-B',str(R/'pg514_reference_schema_test.py')],check=True)
log=W/'pg516-terminal-handoff-v1.private.log';exit_file=W/'pg516-terminal-handoff-v1.exit';source=W/'pg516-terminal-handoff-v1.source.sha256'
assert not log.exists() and not exit_file.exists() and not source.exists();raw=R.joinpath('pg516_terminal_owned_handoff.py').read_bytes()
with source.open('x') as f:f.write(hashlib.sha256(raw).hexdigest()+'\n')
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
with log.open('xb') as f:r=subprocess.run(ssh,input=raw,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with exit_file.open('x') as f:f.write(str(r.returncode)+'\n')
print(json.dumps({'run':'PG516-terminal-handoff-v1','actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'oldCloseUNKNOWN':True,'oldParent143Retained':True,'businessActions0':True}))
raise SystemExit(r.returncode)
