"""BUG747 existing Root stage read-only exact-set/metadata/byte proof; no overwrite."""
import hashlib,json,pathlib,subprocess,os,re
os.umask(0o077)
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
paths=list((W/'pg469-completed-tools-v2').glob('*.class'))+[R/'tools/quality/vm/050_s1'/name for name in ['pg469_live_peer_check.py','pg469_owned_stop.py','pg466_term_witness.py','pg457_stable_actor.py','pg462_observer_identity.py']]
assert len(paths)==8 and all(re.fullmatch(r'[A-Za-z0-9_$]+\.(class|py)',p.name) for p in paths)
expected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};assert len(expected)==len(paths)
payload='EXPECTED='+repr(expected)+'\n'+r'''import pathlib,hashlib,stat,os
assert os.geteuid()==0
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg469-completed-tools-v1')
s=root.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o700
assert set(p.name for p in root.iterdir())==set(EXPECTED)
for name,sha in EXPECTED.items():
 p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o400
 assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
print('PG469_COMPLETED_STAGE_CLOSED exact8Files=true innerClassLiteral=true owner400=true noReinstall=true servicesMutation0=true')
'''
result=subprocess.run(['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg469-completed-stage-check-v1.private.log').open('xb') as f:f.write(result.stdout);f.write(result.stderr)
assert result.returncode==0
assert result.stdout.startswith(b'PG469_COMPLETED_STAGE_CLOSED ')
print(result.stdout.decode(),end='')
