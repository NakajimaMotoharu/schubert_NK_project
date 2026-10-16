"""Qualify the preserved raw24 with independent new-day oracle; never rerun business or SQL."""
import inspect
import json
import pg4632_current_new_day_rows_oracle as oracle
import pg4584_current_admission_image as admission
from pg4442_failed_current_view_qualification import strict_equal
from pg1446_current_cold_stage import W

SLOT='pg4634-current-all24-qualified-v1'


def payload(observed=None,before_hash=None):
    observed=admission.live()if observed is None else observed
    before_hash=admission.before()if before_hash is None else before_hash
    return 'SOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\nBINDING='+repr(observed)+'\nBEFORE_SHA='+repr(before_hash)+'\n'+oracle.source()+'\n'+inspect.getsource(strict_equal)+r'''
import hashlib,os,pathlib,stat
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');saved=base/'pg4628-current-raw24-capture-v1';out=base/'pg4634-current-all24-qualified-v1';require(not os.path.lexists(out));os.umask(0o077);out.mkdir(mode=0o700)
def read(name,digest):
 p=saved/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 metadata=lambda v:(v.st_dev,v.st_ino,v.st_uid,v.st_gid,v.st_mode,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:raw=os.pread(fd,s.st_size+1,0);require(len(raw)==s.st_size and metadata(os.fstat(fd))==metadata(s)and metadata(p.lstat())==metadata(s))
 finally:os.close(fd)
 require(hashlib.sha256(raw).hexdigest()==digest);return raw
br=read('before.private.json',BEFORE_SHA)
ar=read('after.private.json','d6d3a6fe639feb3e898d18b7c5ac6281efe8ef5d4767a7eaf597f3254bbc52f3')
sr=read('sql-stdout.private.jsonl','a2c3238a0b5b50fac2bd556bea696a5bc72805c6655c424106abe592f3c26ad4')
before=json.loads(br)['database']['rows'];after=json.loads(ar);rebuilt={}
for line in sr.splitlines():
 v=json.loads(line);require(v['table']not in rebuilt);rebuilt[v['table']]=v['rows']
require(strict_equal(rebuilt,after['rows']))
mr=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(mr).hexdigest()==BOM and json.loads(mr)['source']['commit']==SOURCE)
result=qualify_current(before,after['rows'],BINDING['run'],BINDING['cutoff'],after['upper'])
value={**result,'actualExit':0,'beforeSha256':hashlib.sha256(br).hexdigest(),'afterSha256':hashlib.sha256(ar).hexdigest(),'rawSqlSha256':hashlib.sha256(sr).hexdigest(),'source':SOURCE,'BOM':BOM,'run':BINDING['run'],'cutoff':BINDING['cutoff'],'upper':after['upper'],'startsStopsSqlReadsWrites':0,'all24SameCapturedImage':True,'rawExported':False,'formalAccepted':False}
encoded=json.dumps(value,sort_keys=True).encode()
with(out/'manifest.safe.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps(value))
'''


def main():
    from pg4586_current_independent_acceptance import TERM
    term=json.loads((W/TERM/'manifest.safe.json').read_bytes())
    if term['actualExit']!=0 or term['source']!=admission.SOURCE or term['result']['genuineRootDone']is not True:raise ValueError('genuine current terminal0 first')
    return admission.execute(SLOT,payload())


if __name__=='__main__':raise SystemExit(main())
