"""Fixed fresh four generations, immutable stage then once owned reverse stop."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from pg1201_current_stop_dispatch import STAGE as previous_stage
from pg1247_fresh_owned_stop_sources import sources,SOURCE,BEFORE,W

P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
OPTIONS=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
SSH=['ssh',*OPTIONS,'-p','22222','ubuntu@127.0.0.1']
GUEST='/var/lib/pgpt-s1-preservation/pg1247-native-tools-v1'
STAGE=previous_stage.replace('pg1201','pg1250').replace('PG1201','PG1250').replace('pg1198','pg1247')
compile(STAGE,'<actual fresh immutable stage>','exec')

def main():
    os.umask(0o077)
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('stage or stop required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed source required')
    action=sys.argv[1]
    frozen=json.loads((W/'pg1248-frozen-v1.safe.json').read_bytes())
    pre=json.loads((W/'pg1249-fresh-stop-preflight-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE or frozen['genuineParentBeforeSha256']!=BEFORE or pre['actualExit']!=0 or pre['privateBeforeSha256']!=BEFORE:
        raise ValueError('actual full current preflight and frozen ABI required')
    target=W/'pg1247-native-tools-v1';files=frozen['fileHashes']
    for name,digest in files.items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('fixed immutable SHA refused')
    for name,raw in sources().items():
        if(target/name).read_text()!=raw:raise ValueError('fixed generated source changed')
    base=W/('pg1250-'+action+'-v1')
    if any(Path(str(base)+s).exists()for s in ['.private.log','.exit','.safe.json']):raise ValueError('new-only dispatch slot required')
    if action=='stage':
        archive=P/'pg1247-native-tools-v1.tar'
        with tarfile.open(archive,'x:')as tar:
            for p in sorted(target.rglob('*')):tar.add(p,arcname=str(p.relative_to(target)),recursive=False)
        remote='/home/ubuntu/pg1250-fixed-stage-v1'
        subprocess.run(SSH+['test ! -e '+remote+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+remote],check=True)
        subprocess.run(['scp',*OPTIONS,'-P','22222',str(archive),'ubuntu@127.0.0.1:'+remote+'/'],check=True)
        commands=[(SSH+['sudo -n python3 -B -'],('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE).encode())]
    else:
        if(W/'pg1250-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable stage required')
        cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1068/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1068/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1068/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1068/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
        commands=[(SSH+[prefix+clazz],None)for clazz in ['Pg1247StopLabelTest','Pg1247NativeArgumentTest','Pg1247NativeStop stop']]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();code=0
    with Path(str(base)+'.private.log').open('xb')as log:
        for args,data in commands:
            r=subprocess.run(args,input=data,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=r.returncode
            if code:break
    with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
    value={'action':action,'actualExit':code,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'oldFailedNormalized':False,'starts0':True,'formalAccepted':False}
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return code

if __name__=='__main__':raise SystemExit(main())
