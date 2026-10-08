"""Current source readonly independent step oracle and private bundle capture. No start/restore/DB write."""
import hashlib,json,os,pathlib,subprocess,sys
os.umask(0o077)
R=pathlib.Path(__file__).parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
payload=r'''import datetime,hashlib,io,json,os,pathlib,stat,subprocess,sys,tarfile
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
old_path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-newrun-preflight-v2/before.private.json');old_raw=old_path.read_bytes();assert hashlib.sha256(old_raw).hexdigest()=='b9a70c2635febf3893b17369af3ddfdf721f040b3d6782423790ee63353bac87';old=json.loads(old_raw)
after_path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg559-terminal-readback-v2/after.private.json');after_raw=after_path.read_bytes();assert hashlib.sha256(after_raw).hexdigest()=='23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677';after=json.loads(after_raw)
preui_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg555-preui-v1/full-rows.private.json').read_bytes();assert hashlib.sha256(preui_raw).hexdigest()=='74a1f06ba7d191fa613292e34760c6b043dddf79c1f0696f0f30e27ff946cce6';preui=json.loads(preui_raw)
sealed=json.loads((old_path.parent/'cleanup-oracle.private.json').read_bytes());assert sealed['source']==old['source']=='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
env={};exec(compile(ORACLE_SRC,'<independent SS341 oracle>','exec'),env)
oracle={'expected':preui['expected'],'inboxExpectedDeleted':sealed['inboxExpectedDeleted']}
root=pathlib.Path('/srv/schubert-nk/backup');run='b7e73994-b951-4696-bdd1-cfbc8a10e734';paths=[p for p in root.iterdir()if p.name.endswith('-'+run)];assert len(paths)==1;bundle=paths[0]
assert stat.S_ISDIR(bundle.lstat().st_mode)and not bundle.is_symlink()and {p.name for p in bundle.iterdir()}=={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'}
values={}
for name in ('MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'):
 p=bundle/name;s=p.lstat();metadata=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns];expected=after['backup'][str(p)];assert metadata==expected['metadata']and stat.S_ISREG(s.st_mode)and s.st_nlink==1 and 0<s.st_size<=16777216
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb')as f:values[name]=f.read()
 assert hashlib.sha256(values[name]).hexdigest()==expected['sha256']and p.lstat()==s
summary=env['validate'](old['rows'],after['rows'],oracle,values['MANIFEST.json'],{k:v for k,v in values.items()if k!='MANIFEST.json'})
m=json.loads(values['MANIFEST.json']);expected_name=env['time'](m['startedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')+'-'+run;assert bundle.name==expected_name
assert hashlib.sha256(pathlib.Path('/etc/schubert-nk/backup-age-recipient').read_bytes()).hexdigest()==m['recipientSha256']
with tarfile.open(fileobj=io.BytesIO(values['config.tar']))as archive:
 members=archive.getmembers();assert {p.name for p in members}=={'common.yml','api.yml','web.yml','batch.yml','api.env','web.env','backup-profile.json','inbox-inspector.env'}and len(members)==8
 for entry in members:
  assert entry.isfile()and not entry.issym()and not entry.islnk();actual=archive.extractfile(entry).read();p=pathlib.Path('/etc/schubert-nk')/entry.name;assert actual==p.read_bytes()
  expected_mode=0o600 if entry.name in ('api.env','web.env')else 0o640;assert entry.mode==expected_mode and entry.uid==0
result=subprocess.run(['/usr/lib/postgresql/18/bin/pg_restore','--list',str(bundle/'schubert_nk.dump')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);assert result.returncode==0
assert all(p in after['backup']and v==after['backup'][p]for p,v in old['backup'].items()if v['sha256']is not None)
assert len(list(root.iterdir()))==len(old['backupOldNames'])+1
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg563-independent-backup-v1');assert not save.exists();save.mkdir(mode=0o700)
summary.update({'configArchiveExactEightAllBytesMatch':True,'dbDumpPgRestoreList0':True,'recipientIndependentFingerprint':True,'allOldBackupFilesPreserved':True,'retentionDeletion0':True,'currentSource':'969d8ded10c0bf5841d9e3a5c531e922caf4a24a','rawExported':False,'actualExit':0})
with(save/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(summary,f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|')as tar:
 for name,data in values.items():
  item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o600;tar.addfile(item,io.BytesIO(data))
'''
bundle=P/'pg563-current-backup-v1.private.tar';log=W/'pg563-backup-capture-v1.private.log';exit_file=W/'pg563-backup-capture-v1.exit'
assert not any(p.exists()for p in (bundle,log,exit_file));subprocess.run(['python3','-B',str(R/'pg563_batch_backup_oracle_test.py')],check=True)
with bundle.open('xb')as output,log.open('xb')as error:
 r=subprocess.run(ssh,input=('ORACLE_SRC='+repr((R/'pg563_batch_backup_oracle.py').read_text())+'\n'+payload).encode(),stdout=output,stderr=error);output.flush();os.fsync(output.fileno());error.flush();os.fsync(error.fileno())
with exit_file.open('x')as f:f.write(str(r.returncode)+'\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'privateEncryptedBundleSha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'rawExported':False,'productionPT0':True}));sys.exit(r.returncode)
