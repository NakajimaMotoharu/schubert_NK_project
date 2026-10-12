"""Direct once transport under real host gate; immutable separate stage/stop.

BUG1165/1167/1168. No nested generated main or shared historical globals.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate
from pg1800_warning_owned_stop_sources import sources,context,SOURCE,TOOLS
from pg1774_warning_owned_stop_dispatch import rebind,prior
from pg1798_warning_recovery_independent_post import payload as post_payload,SLOT as OLD_SLOT

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=rebind(prior.prior.STAGE).replace('1774','1802').replace('1772','1800')
REMOTE='/home/ubuntu/pg1802-fixed-stage-v1'
OPTIONS=['-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(P/'known_hosts'),'-i',str(P/'vm-access')]


def run_action(action):
    if action not in ('stage','stop'):raise ValueError('fixed action required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed source required')
    before,_,_,_=context()
    frozen=json.loads((W/'pg1801-frozen-v1.safe.json').read_bytes())
    post=json.loads((W/OLD_SLOT/'manifest.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE or frozen['genuineParentBeforeSha256']!=before or post['actualExit']!=0 or post['guest']['privateBeforeSha256']!=before:raise ValueError('actual independent full post/frozen ABI required')
    target=W/TOOLS;files=frozen['fileHashes']
    for name,digest in files.items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('immutable complete closure refused')
    for name,raw in sources().items():
        if(target/name).read_text()!=raw:raise ValueError('actual emitted source changed')
    base=W/('pg1802-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ['.private.log','.exit','.safe.json','.requested']):raise ValueError('new-only action required')
    with Path(str(base)+'.requested').open('x')as f:
        json.dump({'action':action,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'replayAllowed':False},f);f.flush();os.fsync(f.fileno())
    directory=os.open(base.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(directory)
    finally:os.close(directory)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();code=0
    if action=='stage':
        archive=P/(TOOLS+'.tar')
        with tarfile.open(archive,'x:')as tar:
            for path in sorted(target.rglob('*')):tar.add(path,arcname=str(path.relative_to(target)),recursive=False)
        subprocess.run(SSH+['test ! -e '+REMOTE+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+REMOTE],check=True)
        subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+REMOTE+'/'],check=True)
        commands=[(SSH+['sudo -n python3 -B -'],('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE).encode())]
    else:
        if(W/'pg1802-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('immutable actual stage required')
        fresh=post_payload().replace(OLD_SLOT,'pg1803-warning-stop-fresh-guard-v1')
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=fresh.encode(),capture_output=True,timeout=120)
        (W/'pg1803-warning-stop-fresh-guard-v1.private.log').write_bytes(r.stderr)
        with(W/'pg1803-warning-stop-fresh-guard-v1.safe.json').open('x')as f:
            json.dump({'actualExit':r.returncode,'guest':json.loads(r.stdout)if r.returncode==0 else None,'payloadSha256':hashlib.sha256(fresh.encode()).hexdigest()},f,sort_keys=True)
        if r.returncode:raise ValueError('fresh full current pre-reservation refused')
        cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
        commands=[(SSH+[prefix+clazz],None)for clazz in ['Pg1800OriginalTupleTest','Pg1800StopLabelTest','Pg1800NativeArgumentTest','Pg1800NativeStop stop']]
    with Path(str(base)+'.private.log').open('xb')as log:
        for args,data in commands:
            r=subprocess.run(args,input=data,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=r.returncode
            if code:break
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    result={'action':action,'actualExit':code,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'managerFailureRetained':True,'oldFailedNormalized':False,'starts0':True,'formalAccepted':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return code


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('only fixed stage/stop allowed')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
