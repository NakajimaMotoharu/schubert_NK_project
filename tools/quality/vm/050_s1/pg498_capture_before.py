"""Fresh Root-private quiescent baseline after PG497 NORMAL invalidation, changes0."""
import datetime,hashlib,json,os,pathlib,subprocess
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
payload=r'''import sys,pathlib,json,os,hashlib
assert os.geteuid()==0
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6');import pg496_timeout_owned as h;h.load_definitions()
assert pathlib.Path('/var/lib/pgpt-s1-preservation/pg497-canonical-invalidation-v1/complete.private').read_text().splitlines()==['allNewScopesReturnedNormally=true','oldCloseNotInferred=true','intentsRetired0=true','currentSameEpochInvalid=true','starts0=true']
assert h.epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),True)
units={u:h.show(u) for u in h.ORDER+h.EXTRA}
for u,v in units.items():assert v['MainPID']==v['ControlPID']=='0' and v['Job']=='';h.kernel_empty(u)
value=h.snapshot();assert value==h.snapshot() and units=={u:h.show(u) for u in units}
value['units']=units;value['current']=str(pathlib.Path('/opt/schubert-nk/current').readlink());assert value['current']=='/opt/schubert-nk/releases/0.1.0-PG489'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-before');assert not root.exists();root.mkdir(mode=0o700)
with (root/'snapshot.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG498_BEFORE sha256='+hashlib.sha256((root/'snapshot.private.json').read_bytes()).hexdigest()+' tables24=true batch442=true currentPG489=true starts0=true')
'''
r=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
with (W/'pg498-capture-before-v1.private.log').open('xb') as f:f.write(r.stdout);f.write(r.stderr)
print(r.stdout.decode(),end='');raise SystemExit(r.returncode)
