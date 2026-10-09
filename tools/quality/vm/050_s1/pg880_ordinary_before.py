"""Fresh second same-day pre-start base, independently anchored to completed first cohort."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg878_terminal_final import payload as previous,W,P
R=Path(__file__).resolve().parent
EXTRA='''
def tree_snapshot(name):
 p=pathlib.Path(name);v={}
 for q in(p,*sorted(p.rglob('*'))):
  s=q.lstat();require(not q.is_symlink()and(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode)))
  v[str(q)]={'metadata':list(metadata9(s)),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()if q.is_file()else None};require(metadata9(q.lstat())==metadata9(s))
 return v
def standard_snapshot():
 snapshot()
 source=pathlib.Path('/var/lib/pgpt-s1-preservation/pg870-ordinary-before-v1/after.private.json').read_bytes();require(hashlib.sha256(source).hexdigest()=='a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980')
 unit_files={}
 for name,expected in json.loads(source)['unitFiles'].items():
  p=pathlib.Path(name);s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_uid==0 and not stat.S_IMODE(s.st_mode)&0o022 and s.st_nlink==1)
  unit_files[name]={'metadata':list(metadata9(s)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};require(metadata9(p.lstat())==metadata9(s)and unit_files[name]==expected)
 require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
 trees={n:tree_snapshot(n)for n in('/run/schubert-nk/startup','/var/lib/schubert-nk/maintenance','/srv/schubert-nk/backup','/srv/schubert-nk/data/transfer')}
 return {'units':after['units'],'configuration':after['configuration'],'rows':after['rows'],'trees':trees,'unitFiles':unit_files,'current':str(release.readlink()),'coverageBefore':tree_snapshot('/run/schubert-nk/pt-coverage'),'ordinaryNoargs':True,'oldOriginalCompleted':True,'oldParent143NotAccepted':True,'priorNewGenuine':True}
'''
def payload(proof,seals,mode='capture',once_body=None):
 assert mode in ('capture','once')
 raw=previous(proof,seals)
 marker="native=snapshot();require(native==snapshot())"
 assert raw.count(marker)==1
 raw=raw.replace('bus=dbus.SystemBus(private=True);',EXTRA+'\nbus=dbus.SystemBus(private=True);')
 if mode=='once':
  assert once_body is not None
  a=raw.index(marker);b=raw.index('\nfinally:',a)
  raw=raw[:a]+'value=standard_snapshot();require(value==standard_snapshot())\n'+once_body+raw[b:]
  raw=raw[:raw.index("\nresult={'actualExit'")]+"\nprint(json.dumps(values));raise SystemExit(r.returncode)\n"
 else:
  raw=raw.replace(marker,'value=standard_snapshot();require(value==standard_snapshot());native=value[\'coverageBefore\']')
  raw=raw.replace('pg878-terminal-final-v1','pg880-ordinary-before-v1').replace('PG878-terminal-final-v1','PG880-ordinary-before-v1')
  marker="with(save/'result.safe.json').open('x')as f:"
  assert raw.count(marker)==1
  raw=raw.replace(marker,"snapshot_raw=json.dumps(value,sort_keys=True).encode()\nwith(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(snapshot_raw);f.flush();os.fsync(f.fileno())\nresult.update(beforeSha256=hashlib.sha256(snapshot_raw).hexdigest(),ordinaryNoargs=True,priorNewGenuine=True)\n"+marker)
 ast.parse(raw);return raw
def inputs():
 proof=json.loads((W/'pg875-completed-readonly-v1.safe.json').read_bytes())
 final=json.loads((W/'pg878-terminal-final-v1.safe.json').read_bytes());assert final['actualExit']==0
 seals={k:v['sha256']for k,v in final['proofHashes'].items()if k in ('before.private.json','after.private.json','parent.private.jsonl','complete.private')}
 frozen=json.loads((W/'pg877-frozen-v1.safe.json').read_bytes());hashes={n:frozen['fileHashes'][n]for n in final['toolHashes']}
 receipt=(W/'pg877-native-tools-v1/pg877_parent_receipt.py').read_text()
 return proof,seals,'HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg878-terminal-final-v1.exit').read_bytes()==b'0\n'
 proof,seals,prefix=inputs();base=W/'pg880-ordinary-before-v1';assert not Path(str(base)+'.private.log').exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 started=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=(prefix+payload(proof,seals)).encode(),capture_output=True,timeout=90)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({k:v for k,v in safe.items()if k not in ('toolHashes','proofHashes')}));raise SystemExit(r.returncode)
if __name__=='__main__':main()
