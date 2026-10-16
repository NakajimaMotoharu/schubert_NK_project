"""One reserved stage or owned candidate-only RO; no publication/start/stop/reload."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import pg3446_current_outbox_ro_dispatch as template
import pg3780_hygiene_ro_sources as role
from pg3782_hygiene_ro_compile import TARGET, generated
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg3784-fixed-stage-v1'
STAGE=role.bind(template.STAGE)


def main():
    if sys.argv[1:]not in (['stage'],['prepare-ro']):raise ValueError('explicit stage or prepare-ro only')
    role.qualify()
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',role.SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('fixed candidate source/operator required')
    fixed=json.loads((W/'pg3782-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0 or fixed['productionSource']!=role.CURRENT or fixed['candidateSource']!=role.SOURCE or fixed['candidateManifestSha256']!=role.BOM:raise ValueError('actual same current/candidate ABI required')
    for name,digest in fixed['fileHashes'].items():
        if hashlib.sha256((TARGET/name).read_bytes()).hexdigest()!=digest:raise ValueError('fixed actual byte changed')
    for name,raw in generated().items():
        if(TARGET/name).read_text()!=raw:raise ValueError('actual composed helper changed')
    action=sys.argv[1];base=W/('pg3784-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ['.begin.safe.json','.private.log','.safe.json','.exit']):raise ValueError('one reserved action only')
    os.umask(0o077);operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    begin={'action':action,'operatorSource':operator,'candidateSource':role.SOURCE,'installedSource':role.CURRENT,'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'RESERVED_NOT_ACCEPTED','formalAccepted':False}
    with Path(str(base)+'.begin.safe.json').open('x')as f:json.dump(begin,f,sort_keys=True)
    with management_gate(P/'current-management-critical.lock'),Path(str(base)+'.private.log').open('xb')as log:
        if action=='stage':
            archive=P/(role.TOOLS+'.tar')
            with tarfile.open(archive,'x:')as tar:
                for p in sorted(TARGET.rglob('*')):tar.add(p,arcname=str(p.relative_to(TARGET)),recursive=False)
            result=subprocess.run(SSH+['test ! -e '+REMOTE+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+REMOTE],stdout=log,stderr=log)
            options=template.old.previous.previous.prior.prior.prior.OPTIONS
            if not result.returncode:result=subprocess.run(['scp',*options,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+REMOTE+'/'],stdout=log,stderr=log)
            if not result.returncode:result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(fixed['fileHashes'])+'\n'+STAGE).encode(),stdout=log,stderr=log)
        else:
            if(W/'pg3784-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable stage required')
            release='/opt/schubert-nk/releases/0.1.0-PG3420'
            cp=':'.join([GUEST,release+'/operations/batch.jar',release+'/operations/lib/*',release+'/api/api.jar',release+'/api/lib/*','/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'])
            prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
            for clazz in ['Pg3780OriginalTupleTest','Pg3780StopLabelTest','Pg3780NativeArgumentTest','Pg3780CurrentIdentityTest','Pg3780InputBoundaryTest',role.CLASS+' prepare-ro']:
                result=subprocess.run(SSH+[prefix+clazz],stdout=log,stderr=log)
                if result.returncode:break
        log.flush();os.fsync(log.fileno())
    observed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    with Path(str(base)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    value={**begin,'actualExit':result.returncode,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completedObservedHead':observed,'sourceQualified':result.returncode==0 and observed==operator,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'candidateHostReadonlyOnly':True,'currentApprovalEpochChanged':False,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
