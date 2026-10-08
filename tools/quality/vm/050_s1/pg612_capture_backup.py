"""Readonly sealed same-day backup copy; secrets stay in private files or memory."""
import hashlib
import io
import json
import os
import pathlib
import subprocess
import tarfile

R = pathlib.Path(__file__).parent
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD = r'''
import ast,datetime,hashlib,io,json,os,pathlib,stat,subprocess,sys,tarfile
os.umask(0o077)
def require(v):
 if not v:raise ValueError('same-day readonly backup capture refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation')
helper=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(helper).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
defs=[n for n in ast.parse(helper).body if isinstance(n,ast.FunctionDef)and n.name in ('metadata','tree','strict')];require(len(defs)==3);exec(compile(ast.Module(body=defs,type_ignores=[]),'<sealed tree>','exec'),globals())
oldraw=strict(base/'pg605-fresh-parent-v2/before.private.json',0o600,33554432);require(hashlib.sha256(oldraw).hexdigest()=='f6b3a93a9ad83396098fea7bbabef6fb03ca47b5e9a0e4e4bac0902f7b5ad8be');old=json.loads(oldraw)
raw=strict(base/'pg609-completed-readonly-v1/before.private.json',0o600,33554432);require(hashlib.sha256(raw).hexdigest()==AFTER_SHA);after=json.loads(raw);require(after['genuineCompletion']['genuinePid1StartDone']and after['genuineCompletion']['genuineRootDone']and after['source']=='23b14a44b10504172e030bbd6625926bf049fb5c');after['backup']=after['trees']['backup']
require(old['source']=='23b14a44b10504172e030bbd6625926bf049fb5c')
root=pathlib.Path('/srv/schubert-nk/backup');require(tree(root)==after['backup'])
require(all(after['backup'].get(k)==v for k,v in old['backup'].items()if v['sha256']is not None))
env={};exec(compile(ORACLE,'<independent SS341 two backup steps>','exec'),env);run=env['RUN']
paths=[p for p in root.iterdir()if p.name.endswith('-'+run)];require(len(paths)==1);bundle=paths[0]
require(stat.S_ISDIR(bundle.lstat().st_mode)and not bundle.is_symlink()and {p.name for p in bundle.iterdir()}=={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'})
values={}
for name in ('MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'):
 p=bundle/name;m=metadata(p);expected=after['backup'][str(p)];require(m==expected['metadata']and stat.S_ISREG(m[4])and m[5]==1 and 0<m[6]<=16777216)
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb')as f:values[name]=f.read()
 require(m==metadata(p)and hashlib.sha256(values[name]).hexdigest()==expected['sha256'])
sealed=json.loads(strict(base/'pg605-fresh-parent-v2/cleanup-oracle.private.json',0o600,33554432));oracle={'expected':sealed['expected'],'inboxExpectedDeleted':sealed['expected']['inbox_scan_candidates']}
summary=env['validate'](old['rows'],after['rows'],oracle,values['MANIFEST.json'],{k:v for k,v in values.items()if k!='MANIFEST.json'})
m=json.loads(values['MANIFEST.json']);require(bundle.name==env['time'](m['startedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')+'-'+run)
require(hashlib.sha256(pathlib.Path('/etc/schubert-nk/backup-age-recipient').read_bytes()).hexdigest()==m['recipientSha256'])
with tarfile.open(fileobj=io.BytesIO(values['config.tar']))as archive:
 members=archive.getmembers();require(len(members)==8 and {v.name for v in members}=={'common.yml','api.yml','web.yml','batch.yml','api.env','web.env','backup-profile.json','inbox-inspector.env'})
 for entry in members:
  require(entry.isfile()and not entry.issym()and not entry.islnk()and entry.uid==0 and entry.mode==(0o600 if entry.name in ('api.env','web.env')else 0o640))
  p=pathlib.Path('/etc/schubert-nk')/entry.name;before=metadata(p);require(archive.extractfile(entry).read()==p.read_bytes()and metadata(p)==before)
result=subprocess.run(['/usr/lib/postgresql/18/bin/pg_restore','--list',str(bundle/'schubert_nk.dump')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30);require(result.returncode==0)
require(tree(root)==after['backup'])
summary.update(actualExit=0,configEightAllBytes=True,dbDumpPgRestoreList0=True,recipientFingerprint=True,allOldBackupFilesPreserved=True,startsStopsReloadsSqlWrites=0,formalAccepted=False,rawExported=False)
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|')as tar:
 for name,data in {**values,'result.safe.json':json.dumps(summary).encode()}.items():
  entry=tarfile.TarInfo(name);entry.size=len(data);entry.mode=0o600;tar.addfile(entry,io.BytesIO(data))
'''


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain']) == b''
    target = W / 'pg612-current-backup-v1'
    bundle = P / 'pg612-current-backup-v1.private.tar'
    assert not any(os.path.lexists(p) for p in (target, bundle))
    target.mkdir(mode=0o700)
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes', '-oStrictHostKeyChecking=yes',
           '-oUserKnownHostsFile=' + str(P / 'known_hosts'), '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    proof=json.loads((W/'pg609-completed-readonly-v1.safe.json').read_bytes())
    assert proof['actualExit']==0 and proof['productionSource']=='23b14a44b10504172e030bbd6625926bf049fb5c'
    after_sha=proof['beforeSha256'];assert len(after_sha)==64 and all(c in '0123456789abcdef'for c in after_sha)
    with bundle.open('xb') as output, (target / 'capture.private.log').open('xb') as error:
        result = subprocess.run(ssh, input=('AFTER_SHA='+repr(after_sha)+'\nORACLE=' + repr((R / 'pg612_batch_backup_oracle.py').read_text()) + '\n' + PAYLOAD).encode(),
                                stdout=output, stderr=error, timeout=90)
        for f in (output, error):
            f.flush()
            os.fsync(f.fileno())
    with (target / 'capture.exit').open('x') as f:
        f.write(str(result.returncode) + '\n')
    assert result.returncode == 0
    with tarfile.open(bundle) as archive:
        members = archive.getmembers()
        assert len(members) == 5 and all(m.isfile() for m in members)
        summary = json.loads(archive.extractfile('result.safe.json').read())
        manifest = json.loads(archive.extractfile('MANIFEST.json').read())
        cipher = archive.extractfile('credentials.tar.age').read()
    age = pathlib.Path('/home/mini/codex/project1/work/toolchain/age-1.2.1/root/usr/bin')
    public = subprocess.run([str(age / 'age-keygen'), '-y', str(P / 'pg381-backup-age.key')], capture_output=True, timeout=15)
    assert public.returncode == 0 and hashlib.sha256(public.stdout).hexdigest() == manifest['recipientSha256']
    plain = subprocess.run([str(age / 'age'), '-d', '-i', str(P / 'pg381-backup-age.key')], input=cipher, capture_output=True, timeout=30)
    assert plain.returncode == 0 and 0 < len(plain.stdout) <= 16777216
    from pg563_verify_private_credentials_names import NAMES
    with tarfile.open(fileobj=io.BytesIO(plain.stdout)) as archive:
        members = archive.getmembers()
        assert len(members) == 17 and {m.name for m in members} == set(NAMES)
        assert all(m.isfile() and not m.issym() and not m.islnk() and m.uid == 0 and m.mode == 0o600 for m in members)
        hashes = {m.name: hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in members}
    catalog_payload = 'NAMES=' + repr(NAMES) + '\n' + r'''
import hashlib,json,os,pathlib,stat
def meta(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
root=pathlib.Path('/etc/schubert-nk/credentials');result={}
for name in NAMES:
 p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and 0<s.st_size<=1048576
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb')as f:raw=f.read()
 assert meta(p.lstat())==meta(s);result[name]=hashlib.sha256(raw).hexdigest()
print(json.dumps(result))
'''
    catalog = subprocess.run(ssh, input=catalog_payload.encode(), capture_output=True, timeout=30)
    assert catalog.returncode == 0 and hashes == json.loads(catalog.stdout)
    summary.update(credentialSeventeenAllBytes=True,ageDecryption0=True,privateKeyNeverOnServer=True,plaintextPersisted=False,
                   operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                   productionSource='23b14a44b10504172e030bbd6625926bf049fb5c',privateBundleSha256=hashlib.sha256(bundle.read_bytes()).hexdigest())
    with (target / 'result.safe.json').open('x') as f:
        json.dump(summary,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
