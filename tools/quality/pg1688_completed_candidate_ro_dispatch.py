"""New-only immutable RO operator stage and single prepare-ro, no re-placement."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from pg1446_current_cold_stage import W,P,SSH
from pg1250_fresh_owned_stop_dispatch import OPTIONS
from pg1683_closed_unused_dispatch import STAGE as previous_stage
from pg1686_completed_candidate_ro_sources import sources,TOOLS,SOURCE,BOM,CLASS
from pg1674_critical_management_gate import management_gate

TARGET=W/TOOLS
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=previous_stage.replace('pg1683-fixed-stage-v1','pg1688-fixed-stage-v1').replace('pg1681-completed-unused-tools-v4',TOOLS).replace('PG1683','PG1688')


def main():
    os.umask(0o077)
    if sys.argv[1:]not in (['stage'],['prepare-ro']):raise ValueError('closed stage/prepare-ro action required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    if subprocess.check_output(['git','diff','--name-only','1683dd9f6de00e71d2317d9af3cd50400a37bf4e','--','src','pom.xml']):raise ValueError('qualified Production/test source unchanged required')
    fixed=json.loads((W/'pg1687-frozen-v1.safe.json').read_bytes());post=json.loads((W/'pg1685-unused-candidate-full-post-v1/manifest.safe.json').read_bytes())
    if fixed['actualExit']!=0 or post['actualExit']!=0 or fixed['candidateSource']!=SOURCE or post['candidateSource']!=SOURCE or fixed['candidateManifestSha256']!=BOM or post['candidateManifestSha256']!=BOM:raise ValueError('actual qualified unused candidate/current required')
    files=fixed['fileHashes']
    for name,digest in files.items():
        if hashlib.sha256((TARGET/name).read_bytes()).hexdigest()!=digest:raise ValueError('immutable frozen helper hash changed')
    for name,body in sources().items():
        if(TARGET/name).read_text()!=body:raise ValueError('exact frozen completed-profile source changed')
    action=sys.argv[1];base=W/('pg1688-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ['.begin.safe.json','.private.log','.exit','.safe.json']):raise ValueError('reserved action must not be replayed')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    begin={'action':action,'state':'RESERVED_NOT_ACCEPTED','startedUTC':started,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'candidateSource':SOURCE,'installedSource':fixed['productionSource'],'formalAccepted':False}
    with Path(str(base)+'.begin.safe.json').open('x')as f:json.dump(begin,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with management_gate(P/'current-management-critical.lock'),Path(str(base)+'.private.log').open('xb')as log:
        if action=='stage':
            tools=P/(TOOLS+'.tar')
            with tarfile.open(tools,'x:')as tar:
                for p in sorted(TARGET.rglob('*')):tar.add(p,arcname=str(p.relative_to(TARGET)),recursive=False)
            remote='/home/ubuntu/pg1688-fixed-stage-v1'
            r=subprocess.run(SSH+['test ! -e '+remote+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+remote],stdout=log,stderr=log)
            if r.returncode==0:r=subprocess.run(['scp',*OPTIONS,'-P','22222',str(tools),'ubuntu@127.0.0.1:'+remote+'/'],stdout=log,stderr=log)
            if r.returncode==0:r=subprocess.run(SSH+['sudo -n python3 -B -'],input=('DIGEST='+repr(hashlib.sha256(tools.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE).encode(),stdout=log,stderr=log)
        else:
            if(W/'pg1688-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable new stage required')
            cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1544/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1544/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1544/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1544/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
            prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
            for clazz in ['Pg1686OriginalTupleTest','Pg1686StopLabelTest','Pg1686NativeArgumentTest','Pg1686CurrentIdentityTest','Pg1686InputBoundaryTest',CLASS+' prepare-ro']:
                r=subprocess.run(SSH+[prefix+clazz],stdout=log,stderr=log)
                if r.returncode:break
        log.flush();os.fsync(log.fileno());code=r.returncode
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    value={**begin,'actualExit':code,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'candidateHostReadonlyOnly':True,'currentApprovalEpochChanged':False,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
