"""SSC223 fixed current pair; readonly preflight then separately reserved execute."""
import hashlib,json,os,pathlib,subprocess,sys
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
assert len(sys.argv)==2 and sys.argv[1]in ('preflight','execute');mode=sys.argv[1]
for n in ('pg558_current_terminal_test.py','pg558_binding_test.py'):
 subprocess.run(['python3','-B',str(R/n)],check=True)
if mode=='execute':
 assert (W/'pg558-handoff-preflight-v2.exit').read_bytes()==b'0\n'
 assert (W/'pg558-handoff-preflight-v2.source.sha256').read_text().strip()==hashlib.sha256((R/'pg558_current_terminal_handoff.py').read_bytes()).hexdigest()
base='pg558-handoff-'+mode+'-v2';log=W/(base+'.private.log');exit_file=W/(base+'.exit');source=W/(base+'.source.sha256')
assert not any(p.exists()for p in (log,exit_file,source));raw=(R/'pg558_current_terminal_handoff.py').read_bytes()
with source.open('x')as f:f.write(hashlib.sha256(raw).hexdigest()+'\n');f.flush();os.fsync(f.fileno())
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B - '+mode]
with log.open('xb')as f:r=subprocess.run(ssh,input=raw,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with exit_file.open('x')as f:f.write(str(r.returncode)+'\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'run':base,'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'oldCloseUNKNOWN':True,'businessActions0':True}));raise SystemExit(r.returncode)
