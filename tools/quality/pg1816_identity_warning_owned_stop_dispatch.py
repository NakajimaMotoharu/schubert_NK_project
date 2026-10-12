"""Direct immutable current UUID-preserving owned stop, captured operator source."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1808_warning_identity_bound_sources import sources,context,SOURCE,TOOLS
from pg1802_warning_owned_stop_dispatch import STAGE as PREVIOUS_STAGE,OPTIONS
from pg1814_current_pair_independent_post import payload as post_payload,SLOT as POST_SLOT

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1816-fixed-stage-v1'
STAGE=PREVIOUS_STAGE.replace('pg1802','pg1816').replace('PG1802','PG1816').replace('pg1800','pg1808').replace('Pg1800','Pg1808')


def captured_result(operator,current,exit_code):
    if type(operator)is not str or type(current)is not str or type(exit_code)is not int:raise ValueError('typed source observation required')
    return {'operatorSource':operator,'completedObservedHead':current,'operatorSourceUnchanged':operator==current,'actualExit':exit_code,'formalAccepted':False,'sourceQualified':exit_code==0 and operator==current}


def run_action(action):
    if action not in ('stage','stop'):raise ValueError('fixed action required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator required')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    before,_,_,_=context()
    frozen=json.loads((W/'pg1815-frozen-v1.safe.json').read_bytes())
    post=json.loads((W/POST_SLOT/'manifest.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE or frozen['genuineParentBeforeSha256']!=before or post['actualExit']!=0 or post['guest']['privateBeforeSha256']!=before:raise ValueError('actual fixed ABI and independent current whole post required')
    target=W/TOOLS;files=frozen['fileHashes']
    for name,digest in files.items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('complete immutable closure required')
    for name,raw in sources().items():
        if(target/name).read_text()!=raw:raise ValueError('fixed emitted sources required')
    base=W/('pg1816-'+action+'-v1')
    if any(Path(str(base)+s).exists()for s in ['.requested','.private.log','.exit','.safe.json']):raise ValueError('new only action required')
    with Path(str(base)+'.requested').open('x')as f:json.dump({'action':action,'operatorSource':operator,'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'replayAllowed':False},f);f.flush();os.fsync(f.fileno())
    fd=os.open(base.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();code=0
    if action=='stage':
        archive=P/(TOOLS+'.tar')
        with tarfile.open(archive,'x:')as tar:
            for p in sorted(target.rglob('*')):tar.add(p,arcname=str(p.relative_to(target)),recursive=False)
        subprocess.run(SSH+['test ! -e '+REMOTE+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+REMOTE],check=True)
        subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+REMOTE+'/'],check=True)
        commands=[(SSH+['sudo','-n','python3','-'],('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE).encode())]
    else:
        if(W/'pg1816-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable stage required')
        fresh=post_payload().replace(POST_SLOT,'pg1817-identity-warning-stop-fresh-v1')
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=fresh.encode(),capture_output=True,timeout=120)
        (W/'pg1817-identity-warning-stop-fresh-v1.private.log').write_bytes(r.stderr)
        with(W/'pg1817-identity-warning-stop-fresh-v1.safe.json').open('x')as f:json.dump({'actualExit':r.returncode,'guest':json.loads(r.stdout)if r.returncode==0 else None,'payloadSha256':hashlib.sha256(fresh.encode()).hexdigest()},f,sort_keys=True)
        if r.returncode:raise ValueError('fresh before reservation failed')
        cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
        commands=[(SSH+[prefix+n],None)for n in ['Pg1808OriginalTupleTest','Pg1808StopLabelTest','Pg1808NativeArgumentTest','Pg1808NativeStop stop']]
    with Path(str(base)+'.private.log').open('xb')as log:
        for args,data in commands:
            r=subprocess.run(args,input=data,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=r.returncode
            if code:break
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    current=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    value={**captured_result(operator,current,code),'action':action,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':SOURCE,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'managerFailureRetained':True,'oldFailedNormalized':False,'starts0':True}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return code if code else 0 if value['sourceQualified']else 1


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('fixed stage/stop only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
