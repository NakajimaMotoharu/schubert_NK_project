"""Read only actual immutable before schema/counts; never export its data or start."""
import pg4584_current_admission_image as admission

SLOT='pg4594-actual-before-shape-read-v1'


def payload():
    return "ONCE="+repr(admission.ONCE)+'\nSOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+r'''
import hashlib,json,os,pathlib,stat
require=lambda v:None if v else(_ for _ in()).throw(ValueError('actual before schema refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
p=pathlib.Path('/var/lib/pgpt-s1-preservation')/ONCE/'before.private.json';s=p.lstat()
metadata=lambda v:(v.st_dev,v.st_ino,v.st_uid,v.st_gid,v.st_mode,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 raw=os.pread(fd,s.st_size+1,0);require(len(raw)==s.st_size and metadata(os.fstat(fd))==metadata(s)and metadata(p.lstat())==metadata(s))
finally:os.close(fd)
v=json.loads(raw);require(type(v)is dict)
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
shape={k:{'type':type(value).__name__,'count':len(value)if isinstance(value,(dict,list))else None}for k,value in v.items()}
database={k:{'type':type(value).__name__,'count':len(value)if isinstance(value,(dict,list))else None}for k,value in v.get('database',{}).items()}
require(metadata(p.lstat())==metadata(s)and p.read_bytes()==raw)
print(json.dumps({'actualExit':0,'source':SOURCE,'beforeSha256':hashlib.sha256(raw).hexdigest(),'shape':shape,'databaseShape':database,'rawExported':False,'signalsStartsDbWrites':0,'formalAccepted':False}))
'''


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload()))
