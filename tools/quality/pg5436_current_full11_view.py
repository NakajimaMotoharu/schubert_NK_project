"""Lossless full11 projection from genuine5434 fresh snapshot; no repeated business/DB run."""
import json
from pyflakes.api import check
import pg5434_current_full_preservation as before

W=before.W
SLOT='pg5436-current-full11-view-v2'
FIELDS=('backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native')


def payload():
    outer=json.loads((W/before.SLOT/'manifest.safe.json').read_bytes());v=outer['result']
    if outer['actualExit']!=0 or outer['source']!=before.CURRENT or v['productionSource']!=before.CURRENT or (
        v['nativePhysicalFiles']!=88 or v['normalNewReferences']is not True or v['whole24Full32Signed187AndResourcesUnchanged']is not True):
        raise ValueError('actual fresh5434 original complete source-bound snapshot required')
    raw='SOURCE='+repr(before.CURRENT)+'\nBOM='+repr(before.CURRENT_BOM)+'\nSLOT='+repr(SLOT)+'\nFIELDS='+repr(FIELDS)+'\nSNAPSHOT='+repr(v['beforeSha256'])+'\nBASE_SLOT='+repr(before.SLOT)+'\n'+BODY
    if check(raw,'<strict full11 snapshot projection>'):raise ValueError('complete standalone static0')
    compile(raw,'<no repeated DB/native or placement authority>','exec')
    return raw


BODY=r'''
import hashlib,json,os,pathlib,stat
os.umask(0o077)
def require(value):
 if not value:raise ValueError('exact5434 full11 projection refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');path=base/BASE_SLOT/'after.private.json'
s=path.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(path))
fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NOATIME)
try:raw=os.pread(fd,s.st_size+1,0);require(os.fstat(fd)==s and path.lstat()==s)
finally:os.close(fd)
require(len(raw)==s.st_size and hashlib.sha256(raw).hexdigest()==SNAPSHOT)
value=json.loads(raw);require(value['source']==SOURCE and value['manifestSha256']==BOM)
view={key:value[key]for key in FIELDS}
require(len(view)==11 and len(view['rows'])==24 and len(view['units'])==10 and sum(p.endswith('.exec')for p in view['native'])==88)
require(all(v['MainPID']==v['ControlPID']=='0'and not v['Job']for v in view['units'].values()))
release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG4980')
manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active')and not list(pathlib.Path('/run/schubert-nk/startup').glob('*.start.intent')))
require(path.read_bytes()==raw and path.lstat()==s)
save=base/SLOT;require(not os.path.lexists(save));save.mkdir(mode=0o700)
projected=json.dumps(view,sort_keys=True).encode()
with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(projected);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':SOURCE,'BOM':BOM,'privateBeforeSha256':hashlib.sha256(projected).hexdigest(),'sealedFull11Fields':11,'tables':24,'unitCount':10,'nativePhysicalFiles':88,'snapshotSha256':SNAPSHOT,'snapshotOrigin':BASE_SLOT,'newDatabaseReads':0,'snapshotReadTimeIsOriginal5434':True,'currentOriginalClosedAndNoIntent':True,'runtimeConfigFilesToRetire':0,'dataOnlyNotRuntimeAuthority':True,'nativeCandidateCredit':False,'formalAccepted':False}))
'''


def main():return before.admission.execute(SLOT,payload(),90)


if __name__=='__main__':raise SystemExit(main())
