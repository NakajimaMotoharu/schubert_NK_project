"""Independent canonical publication/current187 and original full post.

Old DONE/native remain historical, never proof of new Source parent or coverage.
"""
import inspect
import json
import pg1641_completed_current_preflight_v2 as prior
from pg1446_current_cold_stage import W

SLOT='pg1696-completed-publication-full-post-v1'

PUBLIC_AFTER=r'''
publication=base/'pg1694-completed-ordinary-publication-v1'
def publication_private(name):
 p=publication/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return raw
require(publication_private('complete.private')==b'genuineParentDone=true\nfiniteOrdinaryPublication=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsReloadsEpochWrites0=true\noldUnknownNormalized=false\n')
old_after=after
pub_before=publication_private('before.private.json');require(hashlib.sha256(pub_before).hexdigest()=='9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37')
published_raw=publication_private('after.private.json');after=json.loads(published_raw)
require(set(after)==set(old_after)and all(after[k]==old_after[k]for k in old_after if k!='startup'))
tool=base/'pg1691-completed-publication-tools-v1'
for n,d in PUBLICATION_FILES.items():
 p=tool/n;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==d)
import sys
sys.path.insert(0,str(tool))
oracle={};exec(compile((tool/'pg1691_ordinary_publication_contract.py').read_bytes(),'<frozen independent publication oracle>','exec'),oracle)
expected_epoch=publication_private('expected-epoch.private');oracle['canonical_epoch'](expected_epoch)
S=oracle['STARTUP'];A=oracle['APPROVAL'];C=oracle['CURRENT']
phases=[];public_first=None;public_last=None
for p in publication.iterdir():
 match=re.fullmatch(r'finite-(before|epoch|approval|link-staged|exchanged|old-linked-private|release)-([0-9]+)\.private\.json',p.name)
 if not match:continue
 v=json.loads(publication_private(p.name));phase=match.group(1);stamp=int(match.group(2));phases.append((stamp,phase,v))
require(set(x[1]for x in phases)==set(oracle['PHASES']))
phases.sort(key=lambda x:x[0]);require(phases[0][1]=='before'and phases[-1][1]=='release')
lower=phases[0][0];upper=phases[-1][0];public_first=phases[0][2];public_last=phases[-1][2]
oracle['verify'](public_first,public_last,'release',expected_epoch,lower,upper)
startup_old=old_after['startup'];startup_new=after['startup'];require(set(startup_new)==set(startup_old))
for path,row in startup_old.items():
 actual=startup_new[path]
 if path==S:
  require(row['metadata'][:7]==actual['metadata'][:7]and row['sha256']==actual['sha256']is None and all(lower<=actual['metadata'][i]<=upper for i in [7,8]))
 elif path==S+'/epoch.current':
  m=actual['metadata'];require(m[0]==row['metadata'][0]and m[1]!=row['metadata'][1]and m[2:7]==[0,0,stat.S_IFREG|0o600,1,len(expected_epoch)]and actual['sha256']==hashlib.sha256(expected_epoch).hexdigest()and all(lower<=m[i]<=upper for i in [7,8]))
 else:require(row==actual)
require(strict(pathlib.Path(S)/'epoch.current',0o600,4096)==expected_epoch)
require(strict(pathlib.Path(A)/'current',0o400,4096)==oracle['NEW_APPROVAL'])
require(pathlib.Path(C,'current').readlink()==pathlib.Path(oracle['NEW_LINK']))
preserved=publication/'current-link.private';old_link=public_first[C][C+'/current'];s=preserved.lstat()
require(stat.S_ISLNK(s.st_mode)and list(metadata9(s))[:8]==old_link['metadata'][:8]and str(preserved.readlink())==oracle['OLD_LINK']and lower<=s.st_ctime_ns<=upper and not os.listxattr(preserved))
require(not pathlib.Path(oracle['PART']).exists())
require(publication_private('refs-prepare.private.log')==b'')
gap=publication_private('observations.private').decode('ascii');require(re.fullmatch(r'maxGapNanos=[0-9]+\n',gap)is not None and int(gap.split('=')[1])<30000000000)
'''


def payload():
    fixed=json.loads((W/'pg1693-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0:raise ValueError('actual qualified publication tools required')
    raw=prior.payload()
    marker='bus=dbus.SystemBus(private=True);manager='
    index=raw.index(marker)
    raw='PUBLICATION_FILES='+repr(fixed['fileHashes'])+'\n'+raw[:index]+PUBLIC_AFTER+'\n'+raw[index:]
    raw=raw.replace("'/opt/schubert-nk/releases/0.1.0-PG1544'and hashlib.sha256(manifest).hexdigest()=='e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'", "'/opt/schubert-nk/releases/0.1.0-PG1638'and hashlib.sha256(manifest).hexdigest()=='195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'")
    raw=raw.replace("data['source']['commit']=='4d6bcbddb417b76d27e52d5d9640752c300edccf'", "data['source']['commit']=='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'")
    raw=raw.replace("str(base/'pg1544-manifest.sig')", "str(base/'pg1638-manifest.sig')")
    raw=raw.replace("require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')", "require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1638')")
    raw=raw.replace('pg1641-completed-current-before-v2',SLOT)
    raw=raw.replace("'rawExported':False", "'ordinaryPublicationIndependentPost':True,'canonicalInvalidEpochVerified':True,'newApprovalCurrentAndOldLinkPrivateVerified':True,'oldReceiptBug1154PreservedNotInferred':True,'newSourceParentNotStarted':True,'oldNativeNotAppliedToNewSource':True,'rawExported':False")
    compile(raw,'<whole canonical current publication and original preserved post>','exec')
    return raw


def main():
    actual=json.loads((W/'pg1695-activate-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['currentApprovalEpochChanged']is not True or actual['candidateSource']!='2741c4546afad6c1e8b6efbd53dfb58144edf7bb':raise ValueError('actual completed ordinary publication required')
    code=inspect.getsource(prior.prior.main).replace('pg1639-completed-current-before-v1',SLOT)
    ns={**prior.prior.__dict__,'payload':payload}
    exec(compile(code,'<new independent publication full post transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
