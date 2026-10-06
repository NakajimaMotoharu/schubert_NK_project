"""SSC198 one reserved ordinary same-run start; never repeat an unknown delivery."""
import hashlib,json,pathlib,subprocess,os
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='bab704707b8fd7e0dc7581c4489f0892236efe73';DIGEST='a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286'
assert (W/'pg479-six-full-v1.source').read_text().strip()==SOURCE and (W/'pg479-six-full-v1.exit').read_text().strip()=='0'
assert (W/'pg481-parent-observer-v1.started').exists() and not (W/'pg481-parent-observer-v1.exit').exists()
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
PAYLOAD=r'''import ast,datetime,hashlib,json,os,pathlib,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-prepared-resume-acceptance')
assert (save/'complete.private').read_bytes()==b'preparedResumeAccepted=true\nallNewScopesReturnedNormally=true\noriginalRunCutoffUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n'
current=pathlib.Path('/opt/schubert-nk/current');assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG479')
assert hashlib.sha256((current/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()==DIGEST and json.loads((current/'RELEASE-MANIFEST.json').read_bytes())['source']['commit']==SOURCE
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
defs=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name in ['require','command','metadata','tree','show','rows','kernel']];assert len(defs)==7
import stat
exec(compile(ast.Module(body=defs,type_ignores=[]),'<fixed readonly prestart>','exec'),globals())
before=json.loads((save/'after.private.json').read_text());previous=before;UNITS=list(before['units']);assert len(UNITS)==10
for unit in UNITS:
 assert show(unit,set(before['units'][unit]))==before['units'][unit];kernel(unit)
 assert show(unit,set(before['configuration'][unit]))==before['configuration'][unit]
for key,path in [('original','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('transfer','/srv/schubert-nk/data/transfer'),('startup','/run/schubert-nk/startup'),('native','/run/schubert-nk/pt-coverage'),('config','/etc/schubert-nk')]:assert tree(pathlib.Path(path))==before[key]
assert rows()==before['rows']
assert command(['sudo','-n','-u','postgres','psql','-X','-q','-A','-t','-d','schubert_nk','-c',"select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_api','schubert_web','schubert_inspector'); select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"],4096).splitlines()==[b'0',b'0']
request=pathlib.Path('/run/schubert-nk/backup-request');assert {p.name for p in request.iterdir()}=={'backup-request'}
assert hashlib.sha256((request/'backup-request').read_bytes()).hexdigest()==before['request']['sha256'] and metadata(request/'backup-request')==before['request']['metadata']
oracle=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2/cleanup-oracle.private.json').read_text());cutoff=datetime.datetime.fromisoformat('2026-10-06T06:28:43.734078+00:00');assert oracle['sameThroughoutAdmissionWindow'] and datetime.datetime.fromisoformat(oracle['bounds']['lower'])<=cutoff<=datetime.datetime.fromisoformat(oracle['bounds']['upper'])
fd=os.open(save/'external-start-guard.private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'w') as f:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':SOURCE,'manifestSha256':DIGEST,'run':'49437eda-1681-43a9-883a-424eb55a6166','sameCutoff':True,'originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True},f);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],text=True,timeout=5)
d=dict(line.split('=',1) for line in raw.splitlines());d.update(clientExit=r.returncode,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),clientSuccessIsNotParentSuccess=True)
fd=os.open(save/'external-start-issued.private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'w') as f:json.dump(d,f);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps(d));raise SystemExit(r.returncode)
'''
r=subprocess.run(SSH+['sudo -n python3 -B -'],input=('SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\n'+PAYLOAD).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg481-external-resume-v1.private.log').open('xb') as f:f.write(r.stdout);f.write(r.stderr)
print(r.stdout.decode(),end='')
if r.returncode:print('PG481_RESUME_REFUSED actual='+str(r.returncode)+' priorGuardRequiresReattachment=true privateDiagnostics=true')
raise SystemExit(r.returncode)
