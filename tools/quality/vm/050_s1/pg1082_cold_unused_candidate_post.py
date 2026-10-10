"""Independent whole current and unused signed candidate post; readonly/no authority."""
import ast
import json
from pg1066_cold_prepared_post_v2 import payload as prepared
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W

CHECK=r'''
 import stat,grp
 root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1068')
 assert not root.is_symlink()
 raw=(root/'RELEASE-MANIFEST.json').read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'
 data=json.loads(raw)
 assert data['source']['commit']=='d5b00104280028d9ea81b44c1d1c805f3c2861ed'and data['release']=='0.1.0-PG1068'
 assert data['versions']['schema']=='028'and len(data['artifacts'])==187 and len(data['migrations'])==29
 sums={row['path']:row['sha256']for row in data['artifacts']};assert len(sums)==187
 sums['RELEASE-MANIFEST.json']=hashlib.sha256(raw).hexdigest()
 canonical=''.join(sums[name]+'  '+name+'\n'for name in sorted(sums)).encode('ascii')
 assert (root/'SHA256SUMS').read_bytes()==canonical
 expected=set(sums)|{'SHA256SUMS'}
 directories={str(p)for name in expected for p in pathlib.PurePosixPath(name).parents if str(p)!='.'}
 assert {p.relative_to(root).as_posix()for p in root.rglob('*')}==expected|directories
 gid=grp.getgrnam('schubert').gr_gid;assert gid==986
 for p in (root,*root.rglob('*')):
  s=p.lstat();relative=p.relative_to(root).as_posix()
  executable=relative in ('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
  assert not p.is_symlink()and not os.listxattr(p)and s.st_uid==0 and s.st_gid==gid
  assert stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode)and s.st_nlink==1
  assert stat.S_IMODE(s.st_mode)==(0o750 if p.is_dir()or executable else 0o640)
 for row in data['artifacts']:
  p=root/row['path'];assert p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 sig=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig');s=sig.lstat()
 assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink,s.st_size)==(0,0,0o400,1,64)and not os.listxattr(sig)
 assert hashlib.sha256(sig.read_bytes()).hexdigest()=='5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b'
 subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(root/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 candidate_receipt=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1079-cold-candidate-v1/complete.private').read_bytes()
 assert candidate_receipt==b'allScopesReturnedNormally=true\nunusedCandidatePlacement=true\nepochDbBusinessWrites=0\n'
 assert not any((pathlib.Path('/proc')/str(pid)).exists()for pid in (11678,11704))
 assert raw==(root/'RELEASE-MANIFEST.json').read_bytes()
 assert first==env['snapshot']()and runtime==env['runtime_namespaces']()
'''


def payload():
    actual=json.loads((W/'pg1081-place-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or not actual['unusedColdCandidatePlaced']:raise ValueError('normal actual unused placement required')
    raw=prepared().replace('PG1066-cold-prepared-post-v2','PG1082-cold-unused-candidate-post-v1')
    marker=' for name in reversed(refs):manager.UnrefUnit(name)'
    if raw.count(marker)!=1:raise ValueError('fixed post scope refused')
    raw=raw.replace(marker,CHECK+marker)
    raw=raw.replace("'observerRefsNormalClose':True,","'observerRefsNormalClose':True,'unusedCandidateFullPostVerified':True,'candidateNotActivated':True,")
    ast.parse(raw);return raw


if __name__=='__main__':dispatch('PG1082-cold-unused-candidate-post-v1','pg1082-cold-unused-candidate-post-v1',payload())
