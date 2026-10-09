"""Second same-day fresh run reservation and one ordinary noargs start, never resume old."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg880_ordinary_before import payload as prior,inputs,W,P
from pg872_ordinary_once import BODY as previous_body
def payload():
 proof,seals,prefix=inputs();body=previous_body
 body=body.replace('pg870-ordinary-before-v1','pg880-ordinary-before-v1').replace('pg872-ordinary-once-v1','pg882-ordinary-once-v1')
 before=json.loads((W/'pg880-ordinary-before-v1.safe.json').read_bytes());assert before['actualExit']==0
 body=body.replace('a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980',before['beforeSha256'])
 body=body.replace('with StageReferences():\n','')
 body=body.replace('resources();limited=protected();assert limited==protected();assert standard_snapshot(limited)==before==standard_snapshot(protected());resources()','assert standard_snapshot()==before==standard_snapshot()')
 body=body.replace('assert standard_snapshot(protected())==before;resources()','assert standard_snapshot()==before')
 body=body[:body.index('\nprint(json.dumps(values))')]
 a=body.index('\n assert before[')
 # Keep initial baseline/save/functions outside operation, then indent all under held Ref try.
 leading=body[:a];tail=body[a:]
 leading='\n'.join(' '+line if line else line for line in leading.splitlines())
 once_body=leading+tail
 return prefix+prior(proof,seals,mode='once',once_body=once_body)
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg881-watch-v1.started').exists()and not(W/'pg881-watch-v1.exit').exists()
 watch=W/'pg881-parent-watch-v1.private.jsonl';assert watch.exists()and watch.stat().st_size>0
 base=W/'pg882-ordinary-once-v1';assert not any(Path(str(base)+s).exists()for s in('.private.log','.exit','.safe.json'))
 code=payload();ast.parse(code)
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 started=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=code.encode(),capture_output=True,timeout=90)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'reservationMustBeCheckedBeforeRetry':True,'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(r.returncode)
if __name__=='__main__':main()
