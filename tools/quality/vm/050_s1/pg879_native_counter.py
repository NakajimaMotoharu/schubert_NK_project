"""Same e016 fresh857 + only new1902 eight streams, strictly qualified; no old union."""
import ast,json,os,subprocess
from pathlib import Path
from pg644_native_counter import CATALOG as previous_catalog,code as previous_code
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='e01612fcd7f2752df5ae0836b78538fd5e87f120'
def catalog(before_sha):
 return previous_catalog.replace('pg642-native-stop-v1','pg877-native-stop-v1').replace('c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65',before_sha)
def code(hashes,before_sha,after_sha):
 value=previous_code(hashes)
 for old,new in (
  ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5',SOURCE),
  ('pg642-native-stop-v1','pg877-native-stop-v1'),('pg643-terminal-final-v2','pg878-terminal-final-v1'),
  ('011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c',after_sha),
  ('c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65',before_sha),
  ('104329','189291'),('293d218b06454bd1a8ff350bb93de2d5','09167719cb0445fea8da5a6fdbaa3b0f'),
  ('103062293730','183192933299'),('104759573609','184317014132'),
  ('pg630-retention-factory-six-host-v1','pg857-completed-reference-six-host-v1'),
  ('067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b','fcc7df91f91af8867e2c911fd54e7a834c6d3ef313fc028be0d8c9f417e0d6c6'),
  ("tests']==3468","tests']==3541"),
  ('pg644-current-eight-native-v1','pg879-current-eight-native-v1'),('PG644-current-eight-native-v1','PG879-current-eight-native-v1'),
 ):
  assert old in value,old;value=value.replace(old,new)
 ast.parse(value);return value
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg878-terminal-final-v1.exit').read_bytes()==b'0\n'
 final=json.loads((W/'pg878-terminal-final-v1.safe.json').read_bytes());assert final['actualExit']==0 and final['productionSource']==SOURCE
 seals=final['proofHashes'];before_sha=seals['before.private.json']['sha256'];after_sha=seals['after.private.json']['sha256']
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 hashes=json.loads(subprocess.check_output(ssh,input=catalog(before_sha).encode(),timeout=30));assert len(hashes)==8
 env={'__name__':'fixed_current_e016_counter','__file__':str(R/'pg879_native_counter.py')}
 exec(compile(code(hashes,before_sha,after_sha),'<879 new1902 current e016 source eight only>','exec'),env);env['main']()
if __name__=='__main__':main()
