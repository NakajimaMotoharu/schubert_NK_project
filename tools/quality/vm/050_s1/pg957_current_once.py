"""Current40ef ordinary noargs one durable reservation; never repeat after guard exists."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg954_current_ordinary_before import definitions,prefix,W,P
from pg872_ordinary_once import BODY as previous
def payload():
    body=previous
    for a,b in (('pg870-ordinary-before-v1','pg954-ordinary-before-v1'),('pg872-ordinary-once-v1','pg957-ordinary-once-v1'),('a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980','72d51bd2b7db519b89160881b6b6a1322ee4d8ef68d94bc6b23e6c9724cdb3aa'),('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524')):
        assert a in body,a;body=body.replace(a,b)
    code=prefix()+definitions()+body;ast.parse(code);return code
if __name__=='__main__':
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
    assert json.loads((W/'pg954-ordinary-before-v1.safe.json').read_bytes())['actualExit']==0
    assert(W/'pg956-watch-v1.started').exists()and not(W/'pg956-watch-v1.exit').exists()
    watch=W/'pg956-parent-watch-v1.private.jsonl';assert watch.exists()and watch.stat().st_size>0
    base=W/'pg957-ordinary-once-v1';assert not any(Path(str(base)+s).exists()for s in ('.private.log','.safe.json','.exit'))
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc)
    with Path(str(base)+'.private.log').open('xb')as stream:r=subprocess.run(ssh,input=payload().encode(),stdout=subprocess.PIPE,stderr=stream,timeout=90);stream.flush();os.fsync(stream.fileno())
    safe={'run':'PG957-ordinary-once-v1','actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'formalAccepted':False,'reservationMustBeCheckedBeforeRetry':True}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(r.returncode)
