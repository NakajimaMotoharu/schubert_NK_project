"""Independent new1902 stop full24/full32/source/signature/resource post; read-only."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg877_stop_binding import bindings
from pg613_terminal_final import PAYLOAD as previous
from pg643_terminal_final import SEAL
from pg776_failure_full import ADDITIONAL
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def payload(proof,seals):
 raw=previous
 for old,new in bindings(proof):raw=raw.replace(old,new)
 for old,new in (
  ('pg613-terminal-final-v1','pg878-terminal-final-v1'),('PG613-terminal-final-v1','PG878-terminal-final-v1'),('pg600-manifest.sig','pg862-manifest.sig'),
  ('19b7e618ef04f79aff6cde2c2dbf45269c1f9651efaa44f04d81d84d02b85912',seals['before.private.json']),
  ('a7e90f2973f966def39d473f09274383bc866ad37d98b73c96658ece0a09c849',seals['after.private.json']),
  ('8f31ba931b056ae9776855ac503403e9688eb34316873169eb20205aae3badae',seals['complete.private']),
  ('fbc7033f0d6fd6b6ccd6de656882e2405dc42623b959a69ee86a6074d38e465e',seals['parent.private.jsonl']),
  ('require(p.lstat()==s and hashlib.sha256(raw).hexdigest()==sha)','require(metadata9(p.lstat())==metadata9(s) and not os.listxattr(p) and hashlib.sha256(raw).hexdigest()==sha)'),
  ('for u in UNITS:manager.RefUnit(u);refs.append(u)','for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)'),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 raw=raw.replace('def sealed(name,sha):','def metadata9(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)\ndef sealed(name,sha):')
 pure=(R/'pg775_configuration.py').read_text().replace('FragmentPath,DropInPaths','FragmentPath,DropInPaths,RestrictSUIDSGID,UMask,LimitCORE,MemoryMax,TasksMax')
 raw=raw.replace('bus=dbus.SystemBus(private=True);',pure+'\n'+ADDITIONAL+'\nbus=dbus.SystemBus(private=True);')
 old="require(show(u,configuration_fields())==after['configuration'][u])"
 assert raw.count(old)==1
 raw=raw.replace(old,"require(complete_configuration(command(['systemctl','show',u,'--property='+','.join(sorted(FIELDS))]).decode(),u)==after['configuration'][u])")
 # Configuration FIELDS32 must not replace the independent state FIELDS18.
 raw=raw.replace("after=json.loads(sealed('after.private.json'", "after=json.loads(sealed('after.private.json'")
 raw=raw.replace("require(show(u,FIELDS)==v", "require(show(u,STATE_FIELDS)==v")
 raw=raw.replace(pure+'\n'+ADDITIONAL,'STATE_FIELDS=FIELDS\n'+pure+'\n'+ADDITIONAL)
 marker="native=snapshot();require(native==snapshot())"
 assert raw.count(marker)==1
 raw=raw.replace(marker,"baseline=pathlib.Path('/var/lib/pgpt-s1-preservation/pg875-completed-readonly-v1/before.private.json').read_bytes();require(hashlib.sha256(baseline).hexdigest()=='"+proof['beforeSha256']+"');require(tree(pathlib.Path('/srv/schubert-nk/data/transfer'))==json.loads(baseline)['trees']['transfer']);"+marker)
 raw=raw.replace("require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))","require(not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir()))")
 ast.parse(raw);return raw
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg877-stop-v1.exit').read_bytes()==b'0\n'
 proof=json.loads((W/'pg875-completed-readonly-v1.safe.json').read_bytes());bindings(proof)
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 seals=json.loads(subprocess.check_output(ssh,input=SEAL.replace('pg642-native-stop-v1','pg877-native-stop-v1').encode(),timeout=20))
 build=json.loads((W/'pg877-frozen-v1.safe.json').read_bytes());names=('Pg877NativeStop.class','Pg877NativeStop$References.class','pg877_native_refs.py','pg877_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg877_parent_receipt.py','pg877_durable.py','pg877_configuration.py','pg877_configuration_capture.py')
 hashes={n:build['fileHashes'][n]for n in names};receipt=(W/'pg877-native-tools-v1/pg877_parent_receipt.py').read_text()
 code='HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+payload(proof,seals)
 base=W/'pg878-terminal-final-v1';assert not Path(str(base)+'.private.log').exists()
 started=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=code.encode(),capture_output=True,timeout=90)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({k:v for k,v in safe.items()if k not in ('toolHashes','proofHashes')}));raise SystemExit(r.returncode)
if __name__=='__main__':main()
