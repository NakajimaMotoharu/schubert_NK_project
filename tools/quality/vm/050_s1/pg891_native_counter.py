"""Second current e016 native only; exact new885 end rather than first875 reused."""
import ast,json,os,subprocess
from pathlib import Path
from pg879_native_counter import code as previous_code,catalog as previous_catalog,W,P
R=Path(__file__).resolve().parent
def code(hashes,before_sha,after_sha,end):
 assert type(end)is int and 185542282251<=end<=187342282251
 raw=previous_code(hashes,before_sha,after_sha)
 for old,new in (
  ('pg877-native-stop-v1','pg887-native-stop-v1'),('pg877-stop-v1.exit','pg887-stop-v1.exit'),
  ('pg878-terminal-final-v1','pg890-terminal-final-v1'),('pg879-current-eight-native-v1','pg891-current-eight-native-v1'),('PG879-current-eight-native-v1','PG891-current-eight-native-v1'),
  ('189291','195974'),('09167719cb0445fea8da5a6fdbaa3b0f','75f48ce36cd740e98a801eede7fdbb7f'),
  ('183192933299','185542282251'),('184317014132',str(end)),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 ast.parse(raw);return raw
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg890-terminal-final-v1.exit').read_bytes()==b'0\n'
 final=json.loads((W/'pg890-terminal-final-v1.safe.json').read_bytes());assert final['actualExit']==0 and final['productionSource']=='e01612fcd7f2752df5ae0836b78538fd5e87f120'
 seals=final['proofHashes'];before_sha=seals['before.private.json']['sha256'];after_sha=seals['after.private.json']['sha256'];end=final['genuineCompletion']['endMonotonicUs']
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 hashes=json.loads(subprocess.check_output(ssh,input=previous_catalog(before_sha).replace('pg877-native-stop-v1','pg887-native-stop-v1').encode(),timeout=30));assert len(hashes)==8
 env={'__name__':'fixed_second_e016_counter','__file__':str(R/'pg891_native_counter.py')};exec(compile(code(hashes,before_sha,after_sha,end),'<891 new93cb eight only>','exec'),env);env['main']()
if __name__=='__main__':main()
