"""New-only closed tools + immutable actual watch. No recovery/start/current/permit changes."""
import hashlib, pathlib, subprocess
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
FILES={name:WORK/'pg464-timeout-tool-v2'/name for name in ('Pg464TimeoutIsolation.class','Pg464TimeoutRetirement.class','Pg464CapturedPeers.class')}
FILES['external-watch.private.jsonl']=WORK/'pg463-parent-watch-private-v1.jsonl'
EXPECTED={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in FILES.items()}
OPTIONS=['-i',str(PRIVATE/'vm-access'),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(PRIVATE/'known_hosts')]
SSH=['ssh',*OPTIONS,'-p','22222','ubuntu@127.0.0.1']
subprocess.run(SSH+['set -eu; umask 077; test ! -e /home/ubuntu/pg464-timeout-stage-v2; mkdir /home/ubuntu/pg464-timeout-stage-v2'],check=True)
for name,path in FILES.items():subprocess.run(['scp',*OPTIONS,'-P','22222',str(path),'ubuntu@127.0.0.1:/home/ubuntu/pg464-timeout-stage-v2/'+name],check=True)
PAYLOAD='''import hashlib,json,os,pathlib,stat
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json')
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='0cfd6453948feff4e63912c3169224b0800a0d2c1246f5e06207cab7964386d1'
assert json.loads(manifest.read_bytes())['source']['commit']=='11c1feb1c0b51543f98c28e3f54213274648f06f'
source=pathlib.Path('/home/ubuntu/pg464-timeout-stage-v2');assert {p.name for p in source.iterdir()}==set(EXPECTED)
raws={}
for name,digest in EXPECTED.items():
 p=source/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
 raws[name]=p.read_bytes();assert hashlib.sha256(raws[name]).hexdigest()==digest
target=pathlib.Path('/var/lib/pgpt-s1-preservation/pg464-timeout-tool-v2');capture=pathlib.Path('/var/lib/pgpt-s1-preservation/pg464-parent-timeout-private')
assert not target.exists() and not target.is_symlink();assert capture.stat().st_uid==0 and stat.S_IMODE(capture.stat().st_mode)==0o700
original={*('unit-'+str(i)+'-before.properties' for i in range(9)),'startup-original-metadata.private.json','startup-original.private.tar','current27.private.dump','capture-complete.private.json'}
assert {p.name for p in capture.iterdir()}==original
target.mkdir(mode=0o700)
for name,raw in raws.items():
 p=capture/name if name=='external-watch.private.jsonl' else target/name
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600 if name=='external-watch.private.jsonl' else 0o400)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED[name]
assert {p.name for p in target.iterdir()}==set(EXPECTED)-{'external-watch.private.jsonl'}
assert {p.name for p in capture.iterdir()}==original|{'external-watch.private.jsonl'}
os.chmod(target,0o500)
for p in (target,capture,target.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG464_TIMEOUT_STAGE closedClasses3=true root0500File0400=true privateCapture14=true byteHash=true nativeMutation=false')
'''
r=subprocess.run(SSH+['sudo -n python3 -B -'],input=('EXPECTED='+repr(EXPECTED)+'\n'+PAYLOAD).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(r.stdout.decode(),end='')
if r.returncode:print('PG464_TIMEOUT_STAGE_REFUSED actual='+str(r.returncode)+' privateDiagnostics=true')
raise SystemExit(r.returncode)
