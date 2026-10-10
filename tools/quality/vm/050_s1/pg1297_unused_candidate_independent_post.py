"""Full unchanged current resources plus exact new signed unused candidate only."""
import inspect
import pg1281_current_readonly_guard as previous
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST

BODY=r'''
stage_root=base/'pg1293-unused-stage-v1'
def private_read(name):
 p=stage_root/name;st=p.lstat();require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(st));return raw
require(private_read('complete.private')==b'genuineParentDone=true\nunusedCandidatePlaced=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsReloadsEpochWrites0=true\noldUnknownNormalized=false\n')
stage_before=private_read('before.private.json');stage_after=private_read('after.private.json')
require(json.loads(stage_before)==json.loads(stage_after)==after)
root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
def candidate():
 require(not root.is_symlink())
 manifest=(root/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==CANDIDATE_DIGEST)
 value=json.loads(manifest);require(value['source']['commit']==CANDIDATE_SOURCE and value['release']=='0.1.0-PG1292'and value['versions']['schema']=='028'and len(value['artifacts'])==187 and len(value['migrations'])==29)
 paths={v['path']for v in value['artifacts']};require(len(paths)==187)
 paths|={'RELEASE-MANIFEST.json','SHA256SUMS'}
 require({str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==paths)
 summary={}
 for p in [root,*root.rglob('*')]:
  st=p.lstat();require(not p.is_symlink()and st.st_uid==0 and st.st_gid==986 and not os.listxattr(p))
  if p.is_dir():require(st.st_mode==0o40750)
  else:
   relative=str(p.relative_to(root));executable=relative in ['operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector']
   require(stat.S_ISREG(st.st_mode)and st.st_mode==(0o100750 if executable else 0o100640)and st.st_nlink==1)
  summary[str(p)]=metadata9(st)
 for row in value['artifacts']:
  p=root/row['path'];require(p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
 sums={row['path']:row['sha256']for row in value['artifacts']};sums['RELEASE-MANIFEST.json']=CANDIDATE_DIGEST
 require((root/'SHA256SUMS').read_bytes()==''.join(sums[n]+'  '+n+'\n'for n in sorted(sums)).encode('ascii'))
 sig=base/'pg1292-manifest.sig';st=sig.lstat();require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink,st.st_size)==(0,0,0o400,1,64)and not os.listxattr(sig))
 command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(root/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],4096)
 summary[str(sig)]=metadata9(st)
 return summary,hashlib.sha256(sig.read_bytes()).hexdigest()
first_candidate=candidate();require(first_candidate==candidate())
result.update(run='PG1297-unused-candidate-independent-v1',candidateSource=CANDIDATE_SOURCE,candidateManifestSha256=CANDIDATE_DIGEST,
 candidateSignatureSha256=first_candidate[1],candidateArtifacts=187,candidateNodes=len(first_candidate[0])-1,
 stageBeforeSha256=hashlib.sha256(stage_before).hexdigest(),stageAfterSha256=hashlib.sha256(stage_after).hexdigest(),
 stageCompleteSha256=hashlib.sha256(private_read('complete.private')).hexdigest(),allCurrentAndCandidateObservedTwice=True,
 unusedCandidatePlacedUnderGenuineDone=True,candidateNotCurrent=True,approvalEpochOriginalRowsUnchanged=True,formalAccepted=False)
print(json.dumps(result))
'''


def payload():
    code=previous.payload()
    if code.count('print(json.dumps(result))')!=1:raise ValueError('fixed full current result boundary required')
    code=code.replace('print(json.dumps(result))','')
    # All normal current scopes are already returned. The additional bounded
    # candidate oracle reads no Unit metadata and cannot infer any actor result.
    code+='\nCANDIDATE_SOURCE='+repr(SOURCE)+'\nCANDIDATE_DIGEST='+repr(DIGEST)+'\n'+BODY
    compile(code,'<independent unchanged current and unused candidate>', 'exec');return code


def main():
    env=dict(previous.__dict__);env['payload']=payload
    code=inspect.getsource(previous.main).replace('pg1281-current-readonly-v1','pg1297-unused-candidate-independent-v1')
    exec(compile(code,'<new-only unused candidate full post transport>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
