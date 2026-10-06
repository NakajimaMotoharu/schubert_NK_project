"""New-only immutable observer and recoverable prior native exec preservation, no services."""
import hashlib,pathlib,subprocess,os
os.umask(0o077)
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
files={n:R/'tools/quality/vm/050_s1'/n for n in ['pg478_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py']}
expected={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
subprocess.run(ssh+['test ! -e /home/ubuntu/pg478-observer-stage-v1 && mkdir -m 700 /home/ubuntu/pg478-observer-stage-v1'],check=True)
subprocess.run(scp+[*map(str,files.values()),'ubuntu@127.0.0.1:/home/ubuntu/pg478-observer-stage-v1/'],check=True)
payload='EXPECTED='+repr(expected)+'\n'+r'''import pathlib,hashlib,os,stat,subprocess,json
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG477')
units=['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','artemis.service','caddy.service']
for unit in units:
 raw=subprocess.check_output(['systemctl','show',unit,'-pMainPID','-pControlPID','-pJob'],text=True,timeout=5);v=dict(line.split('=',1) for line in raw.splitlines());assert v['MainPID']==v['ControlPID']=='0' and not v['Job']
 for p in pathlib.Path('/sys/fs/cgroup/system.slice',unit).glob('**/cgroup.procs'):assert not p.read_text().strip()
root=pathlib.Path('/var/lib/pgpt-s1-preservation');tools=root/'pg478-observer-v1';save=root/'pg477-stopped-deploy';stage=pathlib.Path('/home/ubuntu/pg478-observer-stage-v1')
assert not tools.exists() and (root/'pg477-completed-acceptance'/'complete.private').exists() and set(p.name for p in stage.iterdir())==set(EXPECTED)
for n,sha in EXPECTED.items():assert hashlib.sha256((stage/n).read_bytes()).hexdigest()==sha
tools.mkdir(mode=0o700)
for n,sha in EXPECTED.items():
 with (tools/n).open('xb') as f:os.fchmod(f.fileno(),0o400);f.write((stage/n).read_bytes());f.flush();os.fsync(f.fileno())
 assert hashlib.sha256((tools/n).read_bytes()).hexdigest()==sha
data=json.loads((save/'native-before.private.json').read_text());assert len(data['oldExec'])==27
for item in data['oldExec']:
 p=pathlib.Path(item['archive']);assert p.parent==save
 st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1 and st.st_size==item['bytes']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
 source=pathlib.Path(item['origin']);assert hashlib.sha256(source.read_bytes()).hexdigest()==item['sha256']
for p in [tools,save,root]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG477_OBSERVER_PREPARED exact3Root400=true old25ExecAnd2HeapsPreserved=true originalExecCurrentlyUntouched=true starts0=true permits0=true')
'''
run=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg478-observer-stage-v1.private.log').open('xb') as f:f.write(run.stdout);f.write(run.stderr)
print(run.stdout.decode(),end='')
raise SystemExit(run.returncode)
