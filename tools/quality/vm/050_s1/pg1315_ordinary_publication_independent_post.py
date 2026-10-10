"""Independent seven-phase/full protected post; this is observation, not repair."""
import inspect
from pathlib import Path
import pg1281_current_readonly_guard as previous
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST

BODY=r'''
tools=base/'pg1311-native-tools-v1';pub=base/'pg1311-unused-stage-v1'
for name,digest in PUBLICATION_HASHES.items():require(hashlib.sha256((tools/name).read_bytes()).hexdigest()==digest)
sys.path.insert(0,str(tools))
import pg1304_ordinary_publication_contract as finite
from pg1090_cold_finite_capture import direct_tree,path_record
from pg1305_ordinary_exchange_io import linked_attributes
def private_publication(name):
 p=pub/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return raw
complete=private_publication('complete.private')
require(complete==b'genuineParentDone=true\nfiniteOrdinaryPublication=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsReloads0=true canonicalEpochWrites=1\noldUnknownNormalized=false\n')
pub_before=json.loads(private_publication('before.private.json'));pub_after=json.loads(private_publication('after.private.json'))
require(pub_before==after and set(pub_after)==set(after)and all(pub_after[k]==after[k]for k in after if k!='startup'))
expected_epoch=private_publication('expected-epoch.private');finite.canonical_epoch(expected_epoch)
begin=(pub/'expected-epoch.private').stat().st_mtime_ns;end=time.time_ns()
snapshots={phase:[]for phase in finite.PHASES}
for p in pub.glob('finite-*.private.json'):
 m=re.fullmatch(r'finite-(before|epoch|approval|link-staged|exchanged|old-linked-private|release)-(\d+)\.private\.json',p.name);require(m is not None)
 snapshots[m[1]].append((int(m[2]),json.loads(private_publication(p.name))))
require(all(snapshots[p]for p in finite.PHASES))
fixed=snapshots['before'][0][1]
for phase,values in snapshots.items():
 for stamp,value in values:
  require(0<stamp<=end);finite.verify(fixed,value,phase,expected_epoch,begin,end)
public_now={r:direct_tree(r)for r in [finite.STARTUP,finite.APPROVAL,finite.CURRENT]}
finite.verify(fixed,public_now,'release',expected_epoch,begin,end)
require(all(value==public_now for _,value in snapshots['release']))
# Validate legacy recursive startup evidence independently, including any descendants.
legacy_before=after['startup'];legacy_now=pub_after['startup']
require(set(legacy_before)==set(legacy_now))
for path,record in legacy_now.items():
 if path in [finite.STARTUP,finite.STARTUP+'/epoch.current']:
  f=public_now[finite.STARTUP][path];require(record=={'metadata':f['metadata'],'sha256':f['sha256']})
 else:require(record==legacy_before[path])
saved_old=pub/'current-link.private';oldfd=os.open(saved_old,os.O_PATH|os.O_NOFOLLOW|os.O_CLOEXEC);dirfd=os.open(pub,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 old_link=linked_attributes(dirfd,'current-link.private',oldfd)
 finite.verify_retained(finite.CURRENT+'/current',fixed[finite.CURRENT][finite.CURRENT+'/current'],old_link,'release',public_now,begin,end)
finally:os.close(oldfd);os.close(dirfd)
require((pathlib.Path(finite.APPROVAL)/'current').read_bytes()==finite.NEW_APPROVAL and(pathlib.Path(finite.STARTUP)/'epoch.current').read_bytes()==expected_epoch)
'''


def payload():
    code=previous.payload()
    marker="release=pathlib.Path('/opt/schubert-nk/current');manifest="
    if code.count(marker)!=1:raise ValueError('independent current boundary required')
    code=code.replace(marker,BODY+'\n'+marker)
    for old,new in [('0.1.0-PG1068','0.1.0-PG1292'),('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',DIGEST),
                    ('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE),('pg1068-manifest.sig','pg1292-manifest.sig')]:
        code=code.replace(old,new)
    old="for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup')]:require(tree(pathlib.Path(p))==after[k])"
    if code.count(old)!=1:raise ValueError('full protected startup boundary required')
    code=code.replace(old,"for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup')]:require(tree(pathlib.Path(p))==(pub_after[k]if k=='startup'else after[k]))")
    code=code.replace("result.update(run='PG1281-current-readonly-v1',startsStopsReloadsSqlWrites0=True)",
      "result.update(run='PG1315-ordinary-publication-independent-v1',startsStopsReloadsSqlWrites0=True,canonicalEpochWrites=1,finiteSevenPhasesVerified=True,oldLinkedInodePreserved=True,publicationCompleteSha256=hashlib.sha256(complete).hexdigest(),publicationBeforeSha256=hashlib.sha256(private_publication('before.private.json')).hexdigest(),publicationAfterSha256=hashlib.sha256(private_publication('after.private.json')).hexdigest(),formalAccepted=False)")
    compile(code,'<full finite publication independent post>','exec');return code


def main():
    # The qualified transport embeds old immutable current helper hashes and
    # genuine DONE seal; new publication helper hashes are separately frozen.
    import json
    W=previous.transport.W
    if(W/'pg1314-activate-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual normal publication required')
    frozen=json.loads((W/'pg1312-frozen-v1.safe.json').read_bytes())
    hashes={name:frozen['fileHashes'][name]for name in ['pg1304_ordinary_publication_contract.py','pg1305_ordinary_exchange_io.py','pg1083_cold_publication_contract.py','pg1088_cold_exchange_io.py','pg1090_cold_finite_capture.py']}
    env=dict(previous.__dict__);env['payload']=lambda:'PUBLICATION_HASHES='+repr(hashes)+'\n'+payload()
    code=inspect.getsource(previous.main).replace('pg1281-current-readonly-v1','pg1315-ordinary-publication-independent-v1')
    exec(compile(code,'<new-only independent publication transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
