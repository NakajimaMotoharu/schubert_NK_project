"""Independent SS343 six-root host metadata oracle; never permit/authority/Production output."""
import hashlib,json,os,pathlib,stat,subprocess
def uid(name):
    r=subprocess.check_output(['/usr/bin/getent','passwd',name],text=True).strip().split(':')
    assert len(r)==7 and r[0]==name
    return int(r[2])
def gid(name):
    r=subprocess.check_output(['/usr/bin/getent','group',name],text=True).strip().split(':')
    assert len(r)==4 and r[0]==name
    return int(r[2])
fixed=[('ASSET','/srv/schubert-nk/data/assets',uid('schubert-data'),gid('schubert-read'),0o750),
       ('TRANSFER','/srv/schubert-nk/data/transfer',uid('schubert-api'),gid('schubert-web'),0o750),
       ('BACKUP','/srv/schubert-nk/backup',uid('schubert-backup'),gid('schubert-backup'),0o700),
       ('LOG','/var/log/schubert-nk',0,gid('schubert'),0o750),
       ('ARTEMIS','/var/lib/schubert-nk/artemis',uid('schubert-artemis'),gid('schubert-artemis'),0o700),
       ('STAGING','/srv/schubert-nk/staging',uid('schubert-migration'),gid('schubert-migration'),0o700)]
epoch=(pathlib.Path('/run/schubert-nk/startup')/'epoch.current').read_text().splitlines()
assert len(epoch)==8 and epoch[:2]==['NKEPOCH1','state=INVALID'] and epoch[-1]=='permit_sha256=-'
claims=dict(x.split('=',1) for x in epoch[2:])
canonical='NKROOTS1\n'+''.join(k+'='+claims[k]+'\n' for k in ['boot_id','epoch_id','run_id','cutoff_utc','activation_id'])
data=[]; seen=set()
for name,path,owner,group,mode in fixed:
    p=pathlib.Path(path)
    for part in [p,*p.parents]: assert not part.is_symlink()
    before=p.lstat(); assert stat.S_ISDIR(before.st_mode) and before.st_nlink>=2
    assert (before.st_uid,before.st_gid,stat.S_IMODE(before.st_mode))==(owner,group,mode)
    assert before.st_dev>=0 and before.st_ino>0 and (before.st_dev,before.st_ino) not in seen
    seen.add((before.st_dev,before.st_ino))
    assert 'system.posix_acl_access' not in os.listxattr(path)
    fs=json.loads(subprocess.check_output(['/usr/bin/findmnt','--json','--target',path,'--output','FSTYPE,VFS-OPTIONS'],text=True))['filesystems'][0]
    assert fs['fstype']=='ext4' and 'rw' in fs['vfs-options'].split(',') and 'ro' not in fs['vfs-options'].split(',')
    after=p.lstat(); assert (before.st_dev,before.st_ino,before.st_uid,before.st_gid,before.st_mode)==(after.st_dev,after.st_ino,after.st_uid,after.st_gid,after.st_mode)
    canonical+=f'{name}|{path}|{before.st_dev}|{before.st_ino}|{owner}|{group}|{mode:04o}|ext4|0|empty\n'
    data.append({'id':name,'device':before.st_dev,'inode':before.st_ino,'uid':owner,'gid':group,'mode':f'{mode:04o}','hostFilesystem':'ext4','hostReadOnly':False,'aclEmpty':True})
print(json.dumps({'formal':False,'independentOracle':True,'roots':data,'expectedCanonicalSha256':hashlib.sha256(canonical.encode('ascii')).hexdigest(),'scope':'host metadata only; native same-owner/private view/capture return-line separately required'}))
