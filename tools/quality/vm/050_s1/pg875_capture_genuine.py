"""Only actual new0916 parent plus new1902 Root DONE; never old DONE/GC inference."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg653_capture_done import payload as previous
from pg870_ordinary_before import parser_source
from pg775_configuration import configuration_value
from pg776_failure_full import ADDITIONAL
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
RUN='19022204-8a9e-418d-ba2a-9967ff923dc2';CUTOFF='2026-10-09T18:28:14.612111Z';ACT='cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d'
def payload():
 raw=previous(RUN)
 for old,new in (
  ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','e01612fcd7f2752df5ae0836b78538fd5e87f120'),('pg650-fresh-parent-v2','pg872-ordinary-once-v1'),
  ("raw=(fresh/'before.private.json').read_bytes()","raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg870-ordinary-before-v1/after.private.json').read_bytes()"),
  ('ef5312d0e59dbc9cce54d7c19eee35d2c7a2dc78afa325c404e4d2d108f73c22','a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980'),
  ('1826480','3592151'),('095f6d1d7f8442b7b2b44ae59a4314f5','09167719cb0445fea8da5a6fdbaa3b0f'),('111752','189291'),('107901545407','183192933299'),('0.1.0-PG631','0.1.0-PG862'),
  ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'),
  ('pg653-completed-readonly-v1','pg875-completed-readonly-v1'),('PG653-completed-readonly-v1','PG875-completed-readonly-v1'),
  ("require(datetime.datetime.fromisoformat(baseline['bounds']['lower'])<=datetime.datetime.fromisoformat(cutoff.replace('Z','+00:00'))<=datetime.datetime.fromisoformat(baseline['bounds']['upper']))", "require(cutoff=='"+CUTOFF+"')"),
  ("m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)","m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.TABLES=tuple(baseline['rows']);require(len(m.TABLES)==24 and len(baseline['rows']['schubert.batch_runs'])==564)"),
  ('for u in m.UNITS:manager.RefUnit(u);refs.append(u)','for u in m.UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)'),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 marker='require(len(matches)==1);activation=matches[0];';assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"require(activation=='"+ACT+"');")
 pure=(R/'pg775_configuration.py').read_text().replace('FragmentPath,DropInPaths','FragmentPath,DropInPaths,RestrictSUIDSGID,UMask,LimitCORE,MemoryMax,TasksMax')
 raw=raw.replace('bus=dbus.SystemBus(private=True);',pure+'\n'+ADDITIONAL+'\nbus=dbus.SystemBus(private=True);')
 marker="return {'units':units,'rows':data";assert raw.count(marker)==1
 raw=raw.replace(marker,"configuration={u:complete_configuration(m.command(['systemctl','show',u,'--property='+','.join(sorted(FIELDS))]).decode(),u)for u in m.UNITS}\n  "+marker.replace("'rows':data","'configuration':configuration,'rows':data"))
 ast.parse(raw);return raw
if __name__=='__main__':
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg871-watch-v1.exit').read_bytes()==b'0\n'and (W/'pg876-chr-a01-native-v1.exit').read_bytes()==b'0\n'
 observed=json.loads((W/'pg871-parent-watch-v1.private.jsonl').read_bytes().splitlines()[-1]);assert observed['terminalObserved'] and observed['parentExit']=='0' and observed['parentResult']=='success' and set(observed['readyObserved'])==set(observed['rootsCaptured'])=={'api','web'} and observed['caddyTlsLogin200']
 base=W/'pg875-completed-readonly-v1';assert not Path(str(base)+'.private.log').exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=('RECEIPT='+repr((R/'pg609_parent_receipt.py').read_text())+'\n'+payload()).encode(),capture_output=True,timeout=90)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n');f.flush();os.fsync(f.fileno())
 safe={'run':'PG875-completed-readonly-v1','actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.flush();os.fsync(f.fileno())
 print(json.dumps(safe));raise SystemExit(r.returncode)
