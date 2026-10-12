"""Direct immutable RO operation; full actual source closure, no old admission chain."""
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
from pg1865_warning_direct_unused_dispatch import STAGE as previous_stage
from pg1867_warning_candidate_ro_sources import sources,TOOLS,CLASS
from pg1868_warning_candidate_ro_compile import TARGET
from pg1844_warning_unit_full_six import CANDIDATE,OLD
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1870-fixed-stage-v1'
STAGE=previous_stage.replace('pg1865-fixed-stage-v1','pg1870-fixed-stage-v1').replace('pg1860-warning-unused-tools-v1',TOOLS)


def main():
    if sys.argv[1:]not in (['stage'],['prepare-ro']):raise ValueError('closed stage/prepare-ro only')
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',CANDIDATE,'--','src','pom.xml']):raise ValueError('fixed candidate source/operator required')
    fixed=json.loads((W/'pg1868-frozen-v1.safe.json').read_bytes());post=json.loads((W/'pg1866-warning-unused-independent-post-v1/manifest.safe.json').read_bytes())
    if fixed['actualExit']!=0 or post['actualExit']!=0 or fixed['productionSource']!=OLD or fixed['candidateSource']!=CANDIDATE or fixed['candidateManifestSha256']!=post['candidateManifestSha256']:raise ValueError('actual frozen same old/new source required')
    generated=sources(fixed['candidateManifestSha256'],post['privateBeforeSha256'])
    bundle=(W/'pg1860-warning-unused-tools-v1/bundle.safe.json').read_bytes()
    generated['pg1867_native_refs.py']='BUNDLE_HASH='+repr(hashlib.sha256(bundle).hexdigest())+'\n'+generated['pg1867_native_refs.py']
    for name,digest in fixed['fileHashes'].items():
        if hashlib.sha256((TARGET/name).read_bytes()).hexdigest()!=digest:raise ValueError('actual fixed immutable byte required')
    for name,raw in generated.items():
        if(TARGET/name).read_text()!=raw:raise ValueError('actual composed helper changed')
    action=sys.argv[1];base=W/('pg1870-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ['.begin.safe.json','.private.log','.safe.json','.exit']):raise ValueError('one reserved action only')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    begin={'action':action,'operatorSource':operator,'candidateSource':CANDIDATE,'installedSource':OLD,'startedUTC':started,'state':'RESERVED_NOT_ACCEPTED','formalAccepted':False}
    with Path(str(base)+'.begin.safe.json').open('x')as f:json.dump(begin,f,sort_keys=True)
    with management_gate(P/'current-management-critical.lock'),Path(str(base)+'.private.log').open('xb')as log:
        if action=='stage':
            archive=P/(TOOLS+'.tar')
            with tarfile.open(archive,'x:')as tar:
                for p in sorted(TARGET.rglob('*')):tar.add(p,arcname=str(p.relative_to(TARGET)),recursive=False)
            r=subprocess.run(SSH+['test ! -e '+REMOTE+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+REMOTE],stdout=log,stderr=log)
            if not r.returncode:r=subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+REMOTE+'/'],stdout=log,stderr=log)
            if not r.returncode:r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(fixed['fileHashes'])+'\n'+STAGE).encode(),stdout=log,stderr=log)
        else:
            if(W/'pg1870-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable stage required')
            cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
            prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
            for clazz in ['Pg1867OriginalTupleTest','Pg1867StopLabelTest','Pg1867NativeArgumentTest','Pg1867CurrentIdentityTest','Pg1867InputBoundaryTest',CLASS+' prepare-ro']:
                r=subprocess.run(SSH+[prefix+clazz],stdout=log,stderr=log)
                if r.returncode:break
        log.flush();os.fsync(log.fileno())
    observed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    value={**begin,'actualExit':r.returncode,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completedObservedHead':observed,'sourceQualified':r.returncode==0 and observed==operator,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'candidateHostReadonlyOnly':True,'currentApprovalEpochChanged':False,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
