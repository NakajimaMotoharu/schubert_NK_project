"""New-only Root400 placement and one fixed handoff. Unknown outcome is never replayed."""
import datetime,hashlib,json,os,pathlib,subprocess
os.umask(0o077)
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
base=W/'pg497-handoff-native-v2';assert not pathlib.Path(str(base)+'.started').exists()
files={n:(R/'tools/quality/vm/050_s1'/n).read_bytes() for n in ['pg497_owned_handoff.py','pg497_owned_handoff_test.py','pg481_native_owned_stop.py','pg466_term_witness.py','pg471_native_term_witness.py','pg477_unit_references.py']}
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
with pathlib.Path(str(base)+'.started').open('x') as f:f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n');f.flush();os.fsync(f.fileno())
payload=r'''import pathlib,hashlib,os,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg497-handoff-tools-v2');assert not root.exists();root.mkdir(mode=0o700)
for name,raw in FILES.items():
 with (root/name).open('xb') as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
 assert (root/name).read_bytes()==raw
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
subprocess.run(['/usr/bin/python3','-B',str(root/'pg497_owned_handoff_test.py')],check=True)
subprocess.run(['/usr/bin/python3','-B',str(root/'pg497_owned_handoff.py'),'handoff'],check=True)
'''
with pathlib.Path(str(base)+'.private.log').open('xb') as f:
 result=subprocess.run(ssh+['sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 -B -'],input=('FILES='+repr(files)+'\n'+payload).encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
for suffix,value in [('.exit',str(result.returncode)),('.completed',datetime.datetime.now(datetime.timezone.utc).isoformat())]:
 with pathlib.Path(str(base)+suffix).open('x') as f:f.write(value+'\n');f.flush();os.fsync(f.fileno())
print('PG497_NATIVE_HANDOFF actual='+str(result.returncode)+' starts0=true oldCloseNotInferred=true diagnosticsPrivate=true')
raise SystemExit(result.returncode)
