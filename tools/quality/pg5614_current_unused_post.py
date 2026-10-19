"""Independent full11/native94 unused187 post; compile before stage/place."""
import json
from pyflakes.api import check
import pg5608_current_unused_sources as role
import pg5606_current_full_preservation as capture

SLOT='pg5614-current-unused-independent-post-v1'


def payload():
    role.qualify();raw=capture.payload()
    marker='NEW_SLOT='+repr(capture.SLOT)
    if raw.count(marker)!=1:raise ValueError('one new post output identity')
    raw=raw.replace(marker,'NEW_SLOT='+repr(SLOT),1)
    marker="    destination = base / NEW_SLOT"
    if raw.count(marker)!=1:raise ValueError('one still-held new before-write reference boundary')
    raw=raw.replace(marker,'\n'.join('    '+s if s else s for s in EXTRA.splitlines())+'\n'+marker,1)
    marker="with(destination/'before.private.json').open('xb')"
    if raw.count(marker)!=1:raise ValueError('one actual after-image file, no historical before overwrite')
    raw=raw.replace(marker,"with(destination/'after.private.json').open('xb')",1)
    marker="'privateBeforeSha256':hashlib.sha256(encoded).hexdigest()"
    if raw.count(marker)!=1:raise ValueError('one explicit post image SHA')
    raw=raw.replace(marker,"'privateAfterSha256':hashlib.sha256(encoded).hexdigest(),'full11BeforeSha256':EXPECTED_BEFORE_SHA,'candidateSource':EXPECTED_CANDIDATE_SOURCE,'candidateManifestSha256':CANDIDATE_RECORD['manifestSha256'],'candidateUnusedOnly':True,'candidate187SignatureVerified':True,'allFull11BeforeAfterEqual':True",1)
    record=json.loads((role.W/'pg5598-candidate-build-v1.safe.json').read_bytes())
    record={k:record[k]for k in('candidateSource','release','manifestSha256','signatureSha256','artifacts')}
    raw='EXPECTED_CURRENT_SOURCE='+repr(role.CURRENT)+'\nEXPECTED_CANDIDATE_SOURCE='+repr(role.SOURCE)+'\nCANDIDATE_RECORD='+repr(record)+'\nEXPECTED_BEFORE_SHA='+repr(role.BEFORE)+'\nBEFORE_SLOT='+repr(capture.SLOT)+'\n'+raw
    if check(raw,'<independent distinct current/candidate full11 post>'):raise ValueError('all standalone bindings before any stage')
    compile(raw,'<strict independent post prepared before place>','exec')
    return raw


EXTRA=r'''
before_path=base/BEFORE_SLOT/'before.private.json'
s=before_path.lstat()
require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not os.listxattr(before_path))
fd=os.open(before_path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME|os.O_CLOEXEC)
try:before_raw=os.pread(fd,s.st_size+1,0);require(os.fstat(fd)==s and before_path.lstat()==s)
finally:os.close(fd)
require(len(before_raw)==s.st_size and hashlib.sha256(before_raw).hexdigest()==EXPECTED_BEFORE_SHA and json.loads(before_raw)==captured)
require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG5430')
require(data['source']['commit']==EXPECTED_CURRENT_SOURCE and CANDIDATE_RECORD['candidateSource']==EXPECTED_CANDIDATE_SOURCE and EXPECTED_CURRENT_SOURCE!=EXPECTED_CANDIDATE_SOURCE)
candidate_root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG5598')
candidate_raw=(candidate_root/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(candidate_raw).hexdigest()==CANDIDATE_RECORD['manifestSha256'])
candidate_value=json.loads(candidate_raw)
require(candidate_value['source']['commit']==EXPECTED_CANDIDATE_SOURCE and candidate_value['release']=='0.1.0-PG5598' and len(candidate_value['artifacts'])==187)
for item in candidate_value['artifacts']:
    target=candidate_root/item['path'];require(target.resolve().is_relative_to(candidate_root)and not target.is_symlink()and target.is_file())
    require(target.stat().st_size==item['size']and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'])
require(set(str(p.relative_to(candidate_root))for p in candidate_root.rglob('*')if p.is_file())=={r['path']for r in candidate_value['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'})
require(not any(p.is_symlink()for p in candidate_root.rglob('*')))
signature=base/'pg5598-manifest.sig';require(signature.stat().st_size==64 and hashlib.sha256(signature.read_bytes()).hexdigest()==CANDIDATE_RECORD['signatureSha256'])
command(['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate_root/'RELEASE-MANIFEST.json'),'-sigfile',str(signature)],4096)
require(before_path.lstat()==s and before_path.read_bytes()==before_raw)
'''


def qualify_placement(value):
    wanted={'actualExit':0,'action':'place','candidateSource':role.SOURCE,'installedSource':role.CURRENT,
      'unusedPlacementOnly':True,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
    if any(type(value.get(k))is not type(v)or value[k]!=v for k,v in wanted.items()):raise ValueError('genuine distinct current/candidate unused placement receipt required')


def main():
    value=json.loads((role.W/'pg5612-place-v1.safe.json').read_bytes());qualify_placement(value)
    return capture.admission.execute(SLOT,payload(),240)


if __name__=='__main__':raise SystemExit(main())
