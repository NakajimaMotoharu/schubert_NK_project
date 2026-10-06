"""Fixed read-only tool stage; no runtime services or configuration mutation."""
import hashlib,os,pathlib,subprocess,sys
os.umask(0o077)
assert sys.argv[1:] in [['before-terminal'],['after-terminal']]
phase=sys.argv[1];r=pathlib.Path(__file__).resolve().parent
w=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');p=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
f=r/'pg479_archive_readonly_capture.py';sha=hashlib.sha256(f.read_bytes()).hexdigest()
opts=['-i',str(p/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(p/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
root='/var/lib/pgpt-s1-preservation/pg479-readonly-tools-v1'
if phase=='before-terminal':
 subprocess.run(ssh+['test ! -e /home/ubuntu/pg479-readonly-v1 && mkdir -m 700 /home/ubuntu/pg479-readonly-v1 && sudo -n test ! -e '+root],check=True)
 subprocess.run(scp+[str(f),'ubuntu@127.0.0.1:/home/ubuntu/pg479-readonly-v1/'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(ssh+['sudo -n install -d -m 700 '+root+' && sudo -n install -m 400 /home/ubuntu/pg479-readonly-v1/'+f.name+' '+root+'/'],check=True)
assert subprocess.check_output(ssh+['sudo -n sha256sum '+root+'/'+f.name]).decode().split()[0]==sha
log=w/('pg479-readonly-'+phase+'-v1.private.log');assert not log.exists()
run=subprocess.run(ssh+['sudo -n python3 -B '+root+'/'+f.name+' '+phase],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with log.open('xb') as stream:stream.write(run.stdout);stream.write(run.stderr)
print(run.stdout.decode(),end='');print('PG479_READONLY actual='+str(run.returncode)+' privateDiagnostics=true');raise SystemExit(run.returncode)
