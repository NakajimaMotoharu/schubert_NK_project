"""SS341/343 independent complete bundle, old-object retention and SQL postcondition.
Read-only private data never leaves Root; summary contains only counts and hashes.
"""
import hashlib,os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
PAYLOAD=r'''import ast,datetime,hashlib,json,os,pathlib,stat,subprocess,tarfile
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-backup-postcondition');assert not save.exists()
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG479')
release=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json');assert hashlib.sha256(release.read_bytes()).hexdigest()=='a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286'
for u in ['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service','artemis.service','schubert-nk-bootstrap-admin.service']:
 d=dict(r.split('=',1) for r in subprocess.check_output(['systemctl','show',u,'--property=MainPID,ControlPID,Job'],text=True).splitlines());assert d=={'MainPID':'0','ControlPID':'0','Job':''}
source=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();assert hashlib.sha256(source).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
env={'pathlib':pathlib,'stat':stat,'hashlib':hashlib,'require':lambda v: v or (_ for _ in ()).throw(ValueError('private backup mismatch'))}
defs=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in ('metadata','tree')];exec(compile(ast.Module(body=defs,type_ignores=[]),'<pinned all-object capture>','exec'),env)
root=pathlib.Path('/srv/schubert-nk/backup');before=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-pending-codeonly/after.private.json').read_text())['backup'];actual=env['tree'](root);assert len(before)==22
for name,v in before.items():
 if name==str(root):assert actual[name]['metadata'][:5]==v['metadata'][:5] and actual[name]['metadata'][5]==v['metadata'][5]+1
 else:assert actual[name]==v
bundle=root/'20261006-172236-49437eda-1681-43a9-883a-424eb55a6166';files={'schubert_nk.dump','config.tar','credentials.tar.age','MANIFEST.json'}
assert set(actual)-set(before)=={str(bundle),*(str(bundle/n) for n in files)} and {p.name for p in bundle.iterdir()}==files
assert bundle.stat().st_uid==992 and bundle.stat().st_gid==977 and stat.S_IMODE(bundle.stat().st_mode)==0o700
raw=(bundle/'MANIFEST.json').read_bytes();assert raw.endswith(b'\n') and len(raw)==971
manifest=json.loads(raw);assert manifest['format']=='NKBACKUP1' and manifest['database']=='schubert_nk' and manifest['runId']=='49437eda-1681-43a9-883a-424eb55a6166' and manifest['cutoff']=='2026-10-06T06:28:43.734078Z'
assert set(manifest['files'])==files-{'MANIFEST.json'}
for name,claim in manifest['files'].items():
 p=bundle/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and s.st_size==claim['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==claim['sha256']
assert manifest['files']['schubert_nk.dump']['size']==8752947 and sum(manifest['files'][n]['size'] for n in ('config.tar','credentials.tar.age'))==61640
profile=json.loads(pathlib.Path('/etc/schubert-nk/backup-profile.json').read_text());assert all(manifest['versions'][k]==profile[k] for k in manifest['versions']) and manifest['versions']['schema']=='027' and manifest['versions']['jdk']=='25.0.4'
expected={'common.yml','api.yml','web.yml','batch.yml','api.env','web.env','backup-profile.json','inbox-inspector.env'}
with tarfile.open(bundle/'config.tar') as t:
 members=t.getmembers();assert len(members)==8 and {m.name for m in members}==expected and all(m.isfile() and not m.issym() and not m.islnk() for m in members)
 for m in members:
  p=pathlib.Path('/etc/schubert-nk')/m.name;s=p.lstat();assert m.size==s.st_size and m.mode==stat.S_IMODE(s.st_mode) and hashlib.sha256(t.extractfile(m).read()).digest()==hashlib.sha256(p.read_bytes()).digest()
assert (bundle/'credentials.tar.age').read_bytes().startswith(b'age-encryption.org/v1\n')
sql="begin read only;set local timezone='UTC';select to_jsonb(t)::text from schubert.batch_runs t where run_id='49437eda-1681-43a9-883a-424eb55a6166' and step in ('BACKUP_DB','BACKUP_CONFIG') order by id;commit;"
rows=[json.loads(r) for r in subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],timeout=10).splitlines()];assert len(rows)==4
for key,step,count,byte_count in [('databaseStep','BACKUP_DB',1,8752947),('configurationStep','BACKUP_CONFIG',2,61640)]:
 successful=[r for r in rows if r['step']==step and r['status']=='SUCCESS'];assert len(successful)==1;r=successful[0];m=manifest[key]
 assert r['id']==m['id'] and r['attempt']==m['attempt']==2 and datetime.datetime.fromisoformat(r['started_at'])==datetime.datetime.fromisoformat(m['startedAt']) and r['target_count']==r['success_count']==count and r['failure_count']==0 and r['byte_count']==byte_count and r['error_code'] is None and r['error_summary'] is None
failed=[r for r in rows if r['status']=='FAILED'];assert len(failed)==2 and all(r['attempt']==1 and r['error_code']=='ABANDONED' for r in failed)
listing=subprocess.check_output(['/usr/lib/postgresql/18/bin/pg_restore','--list',str(bundle/'schubert_nk.dump')],timeout=30);assert listing.startswith(b';\n; Archive created') and b'TABLE DATA schubert app_users' in listing and b'TABLE DATA schubert_web_session web_http_sessions' in listing
assert actual==env['tree'](root)
save.mkdir(mode=0o700)
with (save/'postcondition.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'bab704707b8fd7e0dc7581c4489f0892236efe73','old':before,'actual':actual,'manifest':manifest,'rows':rows,'dumpListSHA256':hashlib.sha256(listing).hexdigest()},f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'oldPhysical22Preserved':True,'newBundleFourArtifacts':True,'manifestSHA256':hashlib.sha256(raw).hexdigest(),'threeArtifactHashesMatched':True,'eightConfigMembersIndependent':True,'dbPairCommitted1And2':True,'oldPartPreserved':True,'dumpReadableNotRestoreTest':True,'credentialDecryptionNotRun':True,'databaseMutation0':True,'snapshotSHA256':hashlib.sha256((save/'postcondition.private.json').read_bytes()).hexdigest()}))
'''
log=W/'pg481-backup-postcondition-v1.private.log';assert not log.exists();r=subprocess.run(SSH+['sudo -n python3 -B -'],input=PAYLOAD.encode(),capture_output=True)
with log.open('xb') as f:f.write(r.stdout);f.write(r.stderr)
print('PG481_BACKUP_POSTCONDITION actual='+str(r.returncode)+' privateOnly=true')
if r.returncode==0:print(r.stdout.decode(),end='')
raise SystemExit(r.returncode)
