"""Direct SSC283 stage/activate; fixed full graph and actual preownership marker."""
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
from pg1875_warning_ro_marker_dispatch import STAGE as old_stage
from pg1877_warning_publication_sources import sources,TOOLS,CLASS,BOM
from pg1879_warning_publication_compile import TARGET
from pg1844_warning_unit_full_six import CANDIDATE,OLD
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1880-fixed-stage-v1'
STAGE=old_stage.replace('pg1875-fixed-stage-v1','pg1880-fixed-stage-v1').replace('pg1872-warning-candidate-ro-tools-v1',TOOLS)


def main():
    if sys.argv[1:]not in (['stage'],['activate']):raise ValueError('closed stage/activate only')
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',CANDIDATE,'--','src','pom.xml']):raise ValueError('fixed clean candidate/operator required')
    fixed=json.loads((W/'pg1879-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0 or fixed['sourceQualified']is not True or fixed['productionSource']!=OLD or fixed['candidateSource']!=CANDIDATE or fixed['candidateManifestSha256']!=BOM:raise ValueError('actual sameSource frozen publication required')
    generated=sources();bundle=(W/'pg1860-warning-unused-tools-v1/bundle.safe.json').read_bytes()
    generated['pg1877_native_refs.py']='BUNDLE_HASH='+repr(hashlib.sha256(bundle).hexdigest())+'\n'+generated['pg1877_native_refs.py']
    for name,digest in fixed['fileHashes'].items():
        if hashlib.sha256((TARGET/name).read_bytes()).hexdigest()!=digest:raise ValueError('actual immutable byte changed')
    for name,raw in generated.items():
        if(TARGET/name).read_text()!=raw:raise ValueError('actual composed source changed')
    action=sys.argv[1];base=W/('pg1880-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ['.begin.safe.json','.private.log','.safe.json','.exit']):raise ValueError('new-only action required')
    os.umask(0o077);operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    begin={'action':action,'operatorSource':operator,'candidateSource':CANDIDATE,'installedBeforeSource':OLD,'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
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
            if(W/'pg1880-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual new immutable stage required')
            check=subprocess.run(SSH+['sudo','-n','python3','-B',GUEST+'/pg1877_input_preflight.py'],capture_output=True,timeout=20)
            pre={'actualExit':check.returncode,'operatorSource':operator,'matched':check.stdout==b'PG1877_INPUT_CLOSURE_READY\n'and not check.stderr,'stdoutSha256':hashlib.sha256(check.stdout).hexdigest(),'stderrSha256':hashlib.sha256(check.stderr).hexdigest(),'ownerBefore':True}
            with(W/'pg1880-actual-prequal-v1.safe.json').open('x')as f:json.dump(pre,f,sort_keys=True)
            if check.returncode or pre['matched']is not True:raise ValueError('actual preownership marker rejected')
            cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
            prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
            for clazz in ['Pg1877OriginalTupleTest','Pg1877StopLabelTest','Pg1877NativeArgumentTest','Pg1877CurrentIdentityTest','Pg1877InputBoundaryTest','Pg1877TransitionTest',CLASS+' activate']:
                r=subprocess.run(SSH+[prefix+clazz],stdout=log,stderr=log)
                if r.returncode:break
        log.flush();os.fsync(log.fileno())
    observed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    changed=False if action=='stage'else True if r.returncode==0 else None
    value={**begin,'actualExit':r.returncode,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completedObservedHead':observed,'sourceQualified':r.returncode==0 and observed==operator,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'currentApprovalEpochChanged':changed,'unitExchangeAndReload':changed,'startsStopsSqlWrites0':True,'oldFailedNormalized':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
