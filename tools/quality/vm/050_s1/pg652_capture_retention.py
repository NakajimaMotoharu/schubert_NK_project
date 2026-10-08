"""New normal parent readonly full-row/retention evidence, no action authority."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg639_capture_resume import PAYLOAD as TEMPLATE

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload():
    raw=TEMPLATE
    for old,new in (
        ('pg637-fresh-resume-v2','pg650-fresh-parent-v2'),('pg639-resume-post-v2','pg652-retention-post-v1'),
        ('c946eaae7147aff0fb328bfabda0d779133f7c04cc30a9a0427d58ae7da76d2e','ef5312d0e59dbc9cce54d7c19eee35d2c7a2dc78afa325c404e4d2d108f73c22'),
        ('1522744','1826480'),('293d218b06454bd1a8ff350bb93de2d5','095f6d1d7f8442b7b2b44ae59a4314f5'),
        ('104329','111752'),('103062293730','107901545407'),('==504','==514'),('<=504','<=514'),
        ("all(r['status']=='SKIPPED'for r in n['schubert.batch_runs']if r['id']not in {s['id']for s in old['rows']['schubert.batch_runs']})", "all(r['status']==('SUCCESS'if r['step']in ('BACKUP_DB','BACKUP_CONFIG')else'SKIPPED')for r in n['schubert.batch_runs']if r['id']not in {s['id']for s in old['rows']['schubert.batch_runs']})"),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    marker="backup=tree(pathlib.Path('/srv/schubert-nk/backup'));summary=env['validate'](old['rows'],n,old['backup'],backup)"
    replacement=r'''
backup=tree(pathlib.Path('/srv/schubert-nk/backup'))
added=[r for r in n['schubert.batch_runs']if r['id']not in {s['id']for s in old['rows']['schubert.batch_runs']}];require(len(added)==10 and len({r['run_id']for r in added})==1);run=added[0]['run_id']
anchor=strict(pathlib.Path('/var/lib/schubert-nk/maintenance/runs')/(run+'.run'),0o600,72)
bundles=[p for p in pathlib.Path('/srv/schubert-nk/backup').iterdir()if p.name.endswith('-'+run)];require(len(bundles)==1);bundle=bundles[0]
s=bundle.lstat();require(stat.S_ISDIR(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(992,977,0o700)and not os.listxattr(bundle))
require({p.name for p in bundle.iterdir()}=={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'})
values={}
for name in ('MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'):
 file_path=bundle/name;first=metadata(file_path);require(stat.S_ISREG(first[4])and first[5]==1 and 0<first[6]<=16777216 and not os.listxattr(file_path))
 require((first[2],first[3],stat.S_IMODE(first[4]))==((992,977,0o600)if name=='schubert_nk.dump'else(0,0,0o600)))
 fd=os.open(file_path,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb')as f:values[name]=f.read()
 require(metadata(file_path)==first and hashlib.sha256(values[name]).hexdigest()==backup[str(file_path)]['sha256'])
expected=json.loads(strict(fresh/'cleanup-oracle.private.json',0o600,33554432))['retention']
summary=env['validate'](old['rows'],n,old['backup'],backup,expected,values['MANIFEST.json'],{k:v for k,v in values.items()if k!='MANIFEST.json'},anchor,old['bounds'])
require(hashlib.sha256(pathlib.Path('/etc/schubert-nk/backup-age-recipient').read_bytes()).hexdigest()==json.loads(values['MANIFEST.json'])['recipientSha256'])
restore=subprocess.run(['/usr/lib/postgresql/18/bin/pg_restore','--list',str(bundle/'schubert_nk.dump')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30);require(restore.returncode==0)
summary.update(actualDumpList0=True,newFileSecurity=True)
'''
    assert raw.count(marker)==1;raw=raw.replace(marker,replacement)
    raw=raw.replace('pg652-retention-post-v1','pg652-retention-post-v2').replace('PG639-resume-post-v2','PG652-retention-post-v2')
    marker="root.mkdir(mode=0o700)"
    assert raw.count(marker)==1
    return raw.replace(marker,"require(type(p)is dict and p['MainPID']=='1826480')\n"+marker)


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    assert(W/'pg650-start-v2.exit').read_bytes()==b'0\n'
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    code='ORACLE='+repr((R/'pg652_retention_oracle.py').read_text())+'\n'+payload()
    with(W/'pg652-retention-post-v2.private.log').open('xb')as log:
        result=subprocess.run(ssh,input=code.encode(),stdout=subprocess.PIPE,stderr=log);log.flush();os.fsync(log.fileno())
    with(W/'pg652-retention-post-v2.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout);safe['operatorSource']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        with(W/'pg652-retention-post-v2.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        print(json.dumps(safe))
    else:print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256((W/'pg652-retention-post-v2.private.log').read_bytes()).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
