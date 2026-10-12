"""Direct frozen once stop; actual state/config consumers qualified before M/A.

SSC282/BUG1177. Never add virtual configuration fields to state18.
"""
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
from pg1821_warning_parent_configuration_sources import sources,context,SOURCE,TOOLS
from pg1816_identity_warning_owned_stop_dispatch import STAGE as OLD_STAGE,OPTIONS,captured_result
from pg1824_initial_before_pair_independent_post import payload as post_payload,SLOT as POST_SLOT

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1826-fixed-stage-v1'
STAGE=OLD_STAGE.replace('pg1816','pg1826').replace('PG1816','PG1826').replace('pg1808','pg1821').replace('Pg1808','Pg1821')

PARENT_PREQUAL=r'''
import hashlib,json,pathlib,sys
sys.path.insert(0,GUEST)
for name,digest in HASHES.items():
 p=pathlib.Path(GUEST)/name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
import pg1821_native_owned_stop as helper
state=helper.show('schubert-nk-morning-controller.service')
assert len(state)==18 and 'SuccessExitStatus'not in state
config=helper.parent_configuration()
assert set(config)=={'Type','SuccessExitStatus'}and config['Type']==state['Type']
result=helper.qualify_warning_parent({**state,**config},True)
assert result=={'managerFailureRetained':True,'genuinePid1StartDone':False,'stopAuthority':False}
assert helper.show('schubert-nk-morning-controller.service')==state and helper.parent_configuration()==config
print(json.dumps({'actualExit':0,'actualStateFieldCount':18,'actualConfigurationFieldCount':2,'stateHasNoVirtualConfiguration':True,'stateConfigurationStableTwice':True,'managerFailureRetained':True,'genuinePid1StartDone':False,'stopAuthority':False,'MARefDBSignalsStops0':True}))
'''


def run_action(action):
    if action not in ('stage','stop'):raise ValueError('fixed action required')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean source required')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();before,_,_,_=context()
    build=json.loads((W/'pg1825-frozen-v1.safe.json').read_bytes());post=json.loads((W/POST_SLOT/'manifest.safe.json').read_bytes())
    if build['actualExit']!=0 or build['productionSource']!=SOURCE or build['genuineParentBeforeSha256']!=before or post['actualExit']!=0 or post['guest']['privateBeforeSha256']!=before:raise ValueError('actual full current post and fixed ABI required')
    target=W/TOOLS;files=build['fileHashes']
    for name,digest in files.items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('entire immutable closure required')
    for name,raw in sources().items():
        if(target/name).read_text()!=raw:raise ValueError('exact current generated source required')
    base=W/('pg1826-'+action+'-v1')
    if any(Path(str(base)+s).exists()for s in ['.requested','.private.log','.exit','.safe.json']):raise ValueError('new-only action required')
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
        commands=[(SSH+['sudo','-n','python3','-B','-'],('DIGEST='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nFILES='+repr(files)+'\n'+STAGE).encode())]
    else:
        if(W/'pg1826-stage-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual immutable stage required')
        raw='GUEST='+repr(GUEST)+'\nHASHES='+repr(files)+'\n'+PARENT_PREQUAL
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=30)
        (W/'pg1827-parent-two-source-prequalification-v1.private.log').write_bytes(r.stderr)
        with(W/'pg1827-parent-two-source-prequalification-v1.safe.json').open('x')as f:json.dump({'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'guest':json.loads(r.stdout)if r.returncode==0 else None},f,sort_keys=True)
        if r.returncode:raise ValueError('actual deployed state18/config2 refused before ownership')
        fresh=post_payload().replace(POST_SLOT,'pg1828-state-configuration-fresh-whole-v1')
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=fresh.encode(),capture_output=True,timeout=120)
        (W/'pg1828-state-configuration-fresh-whole-v1.private.log').write_bytes(r.stderr)
        with(W/'pg1828-state-configuration-fresh-whole-v1.safe.json').open('x')as f:json.dump({'actualExit':r.returncode,'payloadSha256':hashlib.sha256(fresh.encode()).hexdigest(),'guest':json.loads(r.stdout)if r.returncode==0 else None},f,sort_keys=True)
        if r.returncode:raise ValueError('fresh whole pre-reservation refused')
        cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
        commands=[(SSH+[prefix+n],None)for n in ['Pg1821OriginalTupleTest','Pg1821StopLabelTest','Pg1821NativeArgumentTest','Pg1821NativeStop stop']]
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
