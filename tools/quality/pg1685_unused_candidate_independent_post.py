"""PG1683 independent unchanged-current full post and signed unused187 bytes."""
import inspect
import json
import pg1641_completed_current_preflight_v2 as prior
from pg1446_current_cold_stage import W

SLOT='pg1685-unused-candidate-full-post-v1'
EXTRA=r'''
placed=base/'pg1684-completed-unused-placement-v4'
def held_private(name):
 p=placed/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return raw
require(held_private('complete.private')==b'genuineParentDone=true\nunusedCandidatePlaced=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsReloadsEpochWrites0=true\noldUnknownNormalized=false\n')
for name in ['before.private.json','after.private.json']:
 require(hashlib.sha256(held_private(name)).hexdigest()=='9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37')
gap=held_private('observations.private').decode('ascii');require(re.fullmatch(r'maxGapNanos=[0-9]+\n',gap)is not None and int(gap.split('=')[1])<30000000000)
require(held_private('refs-prepare.private.log')==b'')
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638')
manifest_raw=(candidate/'RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(manifest_raw).hexdigest()=='195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1')
c=json.loads(manifest_raw);require(c['source']['commit']=='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'and c['release']=='0.1.0-PG1638'and c['versions']['schema']=='028'and len(c['artifacts'])==187 and len(c['migrations'])==29)
sums={r['path']:r['sha256']for r in c['artifacts']};require(len(sums)==187)
sums['RELEASE-MANIFEST.json']=hashlib.sha256(manifest_raw).hexdigest()
canonical=''.join(sums[n]+'  '+n+'\n'for n in sorted(sums)).encode('ascii')
require((candidate/'SHA256SUMS').read_bytes()==canonical)
require({p.relative_to(candidate).as_posix()for p in candidate.rglob('*')if p.is_file()}==set(sums)|{'SHA256SUMS'})
for p in [candidate,*candidate.rglob('*')]:
 s=p.lstat();executable=p.relative_to(candidate).as_posix()in ['operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector']
 require(not p.is_symlink()and s.st_uid==0 and s.st_gid==986 and stat.S_IMODE(s.st_mode)==(0o750 if p.is_dir()or executable else 0o640)and not os.listxattr(p))
 if p.is_file():require(s.st_nlink==1)
for row in c['artifacts']:
 p=candidate/row['path'];s=p.lstat();require(s.st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']and metadata9(p.lstat())==metadata9(s))
sig=base/'pg1638-manifest.sig';s=sig.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink,s.st_size)==(0,0,0o400,1,64)and hashlib.sha256(sig.read_bytes()).hexdigest()=='5e32c12cc0231fd9ac307d3ffdfe6428aa53002e0398248cf32362d903d4aca5')
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],4096)
'''


def payload():
    raw=prior.payload().replace('pg1641-completed-current-before-v2',SLOT)
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one independent candidate post boundary required')
    raw=raw.replace(marker,EXTRA+'\n'+marker)
    raw=raw.replace("'rawExported':False", "'unusedCandidate187Verified':True,'candidateSource':'2741c4546afad6c1e8b6efbd53dfb58144edf7bb','candidateManifestSha256':'195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1','rawExported':False")
    compile(raw,'<separate full candidate/current signed post>','exec')
    return raw


def main():
    actual=json.loads((W/'pg1683-place-v2.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['candidateSource']!='2741c4546afad6c1e8b6efbd53dfb58144edf7bb' or actual['currentApprovalEpochChanged']is not False:raise ValueError('actual complete immutable unused placement required')
    code=inspect.getsource(prior.prior.main).replace('pg1639-completed-current-before-v1',SLOT)
    ns={**prior.prior.__dict__,'payload':payload}
    exec(compile(code,'<separate full candidate post transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
