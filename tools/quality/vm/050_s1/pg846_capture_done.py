"""Same current832/new PID1 start+Root DONE under original1800; readonly only."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg653_capture_done import payload as previous
from pg842_resume_post import AFTER
R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
RUN='9de2d03c-28c7-4647-97d9-c66ace06048c'
def payload():
 raw=previous(RUN)
 for a,b in(
  ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','2a0d5aa392c85a1dc12a1cdb423978e8500895b8'),
  ('pg650-fresh-parent-v2','pg844-external-once-v1'),
  ("raw=(fresh/'before.private.json').read_bytes()","raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg841-runtime-resume-v1/after.private.json').read_bytes()"),
  ('ef5312d0e59dbc9cce54d7c19eee35d2c7a2dc78afa325c404e4d2d108f73c22',AFTER),
  ('1826480','3417355'),('095f6d1d7f8442b7b2b44ae59a4314f5','9c08566fff9945a492eaae25559c3084'),
  ('111752','175948'),('107901545407','171417627031'),('0.1.0-PG631','0.1.0-PG832'),
  ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'),
  ('pg653-completed-readonly-v1','pg846-completed-readonly-v1'),('PG653-completed-readonly-v1','PG846-completed-readonly-v1'),
  ("require(datetime.datetime.fromisoformat(baseline['bounds']['lower'])<=datetime.datetime.fromisoformat(cutoff.replace('Z','+00:00'))<=datetime.datetime.fromisoformat(baseline['bounds']['upper']))","require(cutoff=='2026-10-09T05:42:22.532331Z')"),
  ("m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)","m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.TABLES=tuple(baseline['rows']);require(len(m.TABLES)==24 and len(baseline['rows']['schubert.batch_runs'])==554)"),
 ):
  assert a in raw,a;raw=raw.replace(a,b)
 marker="return {'units':units,'rows':data"
 assert raw.count(marker)==1
 fields=(R/'pg847_configuration.py').read_text()
 raw="CONFIG_SCHEMA="+repr(fields)+'\n'+raw
 raw=raw.replace("after=snapshot();", "after=snapshot();")
 raw=raw.replace(marker,"config_env={};exec(compile(CONFIG_SCHEMA,'<independent full32 contract>','exec'),config_env);config_fields=config_env['FIELDS'];require(len(config_fields)==32)\n  configuration={u:show_configuration(u,config_fields)for u in m.UNITS}\n  "+marker.replace("'rows':data","'configuration':configuration,'rows':data"))
 marker=' def snapshot():'
 assert raw.count(marker)==1
 raw=raw.replace(marker," def show_configuration(u,keys):\n  values=dict(l.split('=',1)for l in m.command(['systemctl','show',u,'--property='+','.join(sorted(keys))]).decode().splitlines());require(set(values)==keys);return values\n"+marker)
 ast.parse(raw);return raw

def main():
 os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
 assert(W/'pg843-watch-v1.exit').read_bytes()==b'0\n'and(W/'pg842-resume-post-v1.exit').read_bytes()==b'0\n'
 assert(W/'pg849-chr-a01-native-v1.exit').read_bytes()==b'0\n'
 observed=json.loads((W/'pg843-parent-watch-v1.private.jsonl').read_text().splitlines()[-1])
 assert observed['terminalObserved']and observed['parentExit']=='0'and observed['parentResult']=='success'
 assert set(observed['readyObserved'])==set(observed['rootsCaptured'])=={'api','web'}and observed['caddyTlsLogin200']
 target=W/'pg846-completed-readonly-v1';assert not any(Path(str(target)+s).exists()for s in('.private.log','.exit','.safe.json'))
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 result=subprocess.run(ssh,input=('RECEIPT='+repr((R/'pg609_parent_receipt.py').read_text())+'\n'+payload()).encode(),capture_output=True,timeout=90)
 with Path(str(target)+'.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(target)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n')
 if result.returncode==0:
  safe=json.loads(result.stdout);safe.update(startedUTC=started,endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
  with Path(str(target)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
  print(json.dumps(safe))
 else:print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(result.stderr).hexdigest()}))
 raise SystemExit(result.returncode)
if __name__=='__main__':main()
