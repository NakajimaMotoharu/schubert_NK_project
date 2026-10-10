"""Immutable tools/input stage then once genuine-DONE owned unused placement."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from pg1250_fresh_owned_stop_dispatch import STAGE as previous_stage,SSH,OPTIONS,P,W
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST,BASELINE_SHA,sources

TARGET=W/'pg1293-native-tools-v1'
GUEST='/var/lib/pgpt-s1-preservation/pg1293-native-tools-v1'
REMOTE='/home/ubuntu/pg1295-candidate-input-v1'
STAGE=previous_stage.replace('pg1250-fixed-stage-v1','pg1295-fixed-stage-v1').replace('pg1247-native-tools-v1','pg1293-native-tools-v1').replace('PG1250','PG1295')
compile(STAGE,'<actual immutable completed stage tools>', 'exec')


def main():
    os.umask(0o077)
    if sys.argv[1:]not in (['stage'],['place']):raise ValueError('closed stage or place action required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']):raise ValueError('qualified candidate source must not change')
    action=sys.argv[1];frozen=json.loads((W/'pg1294-frozen-v1.safe.json').read_bytes())
    current=json.loads((W/'pg1296-current-readonly-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or current['actualExit']!=0 or frozen['genuineParentBeforeSha256']!=BASELINE_SHA or frozen['candidateManifestSha256']!=DIGEST:
        raise ValueError('fresh actual current ownership and frozen ABI required')
    if frozen['productionSource']!=current['productionSource']or frozen['candidateSource']!=SOURCE:
        raise ValueError('installed/candidate source separation required')
    files=frozen['fileHashes']
    for name,digest in files.items():
        if hashlib.sha256((TARGET/name).read_bytes()).hexdigest()!=digest:raise ValueError('fixed immutable operator SHA required')
    generated=sources();bundle_raw=(TARGET/'bundle.safe.json').read_bytes()
    generated['pg1293_native_refs.py']='BUNDLE_HASH='+repr(hashlib.sha256(bundle_raw).hexdigest())+'\n'+generated['pg1293_native_refs.py']
    for name,body in generated.items():
        if(TARGET/name).read_text()!=body:raise ValueError('frozen current generated method mismatch')
    base=W/('pg1295-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ['.begin.safe.json','.private.log','.exit','.safe.json']):raise ValueError('reserved actual action must not be replayed')
    archive=P/'pg1295-release-v1.tar';signature=P/'pg1292-manifest-v1.sig';bundle=json.loads(bundle_raw)
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=bundle['archiveSha256']or hashlib.sha256(signature.read_bytes()).hexdigest()!=bundle['signatureSha256']:
        raise ValueError('fixed new signed input bundle required')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    begin={'action':action,'state':'RESERVED_NOT_ACCEPTED','startedUTC':started,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'candidateSource':SOURCE,'installedSource':frozen['productionSource'],'formalAccepted':False}
    with Path(str(base)+'.begin.safe.json').open('x')as f:json.dump(begin,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.private.log').open('xb')as log:
        if action=='stage':
            tools=P/'pg1293-native-tools-v1.tar'
            with tarfile.open(tools,'x:')as tar:
                for path in sorted(TARGET.rglob('*')):tar.add(path,arcname=str(path.relative_to(TARGET)),recursive=False)
            remote_tools='/home/ubuntu/pg1295-fixed-stage-v1'
            args=SSH+['test ! -e '+REMOTE+' && test ! -e '+remote_tools+' && sudo -n test ! -e '+GUEST+' && sudo -n test ! -e /opt/schubert-nk/releases/0.1.0-PG1292 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg1292-manifest.sig && mkdir -m700 '+REMOTE+' '+remote_tools]
            r=subprocess.run(args,stdout=log,stderr=log)
            if r.returncode==0:r=subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),str(signature),str(TARGET/'bundle.safe.json'),'ubuntu@127.0.0.1:'+REMOTE+'/'],stdout=log,stderr=log)
            if r.returncode==0:r=subprocess.run(['scp',*OPTIONS,'-P','22222',str(tools),'ubuntu@127.0.0.1:'+remote_tools+'/'],stdout=log,stderr=log)
            if r.returncode==0:r=subprocess.run(SSH+['sudo -n python3 -B -'],input=('DIGEST='+repr(hashlib.sha256(tools.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE).encode(),stdout=log,stderr=log)
        else:
            if(W/'pg1295-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable tool/input stage required')
            cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1068/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1068/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1068/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1068/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
            prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
            for clazz in ['Pg1293OriginalTupleTest','Pg1293StopLabelTest','Pg1293NativeArgumentTest','Pg1293UnusedStage place']:
                r=subprocess.run(SSH+[prefix+clazz],stdout=log,stderr=log)
                if r.returncode:break
        log.flush();os.fsync(log.fileno());code=r.returncode
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    safe={**begin,'actualExit':code,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'unusedPlacementOnly':True,'currentApprovalEpochChanged':False,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return code


if __name__=='__main__':raise SystemExit(main())
