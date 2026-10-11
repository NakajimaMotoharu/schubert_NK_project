"""Fresh corrected SSC264 family, only after qualified SSC265 handoff.

Compile, stage, prepare are separate explicit new-only commands. Old frozen
tools, failed receipts, current release and successful Root are never replaced.
"""
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import hashlib
import pg1442_current_cold_compile as compiler
import pg1446_current_cold_stage as stage
from pg1441_current_cold_sources import java as original_java
from pg1441_current_cold_refs import source as original_refs

W=compiler.W
TOOLS=W/'pg1450-current-cold-tools-v1'
FROZEN=W/'pg1450-current-cold-frozen-v1.safe.json'
GUEST_TOOLS='/var/lib/pgpt-s1-preservation/pg1450-current-cold-tools-v1'


def replacement(raw):
    for old,new in [('Pg1441CurrentColdPreparation','Pg1450CurrentColdPreparation'),
                    ('pg1441-current-cold-tools-v1','pg1450-current-cold-tools-v1'),
                    ('pg1441-current-cold-prepared-v1','pg1452-current-cold-prepared-v1'),
                    ('pg1441_current_cold_refs.py','pg1450_current_cold_refs.py'),
                    ('PG1441_','PG1452_')]:
        if old not in raw:raise ValueError('explicit new family binding absent')
        raw=raw.replace(old,new)
    return raw


def java():return replacement(original_java())


def observer():
    raw=original_refs()
    for old,new in [('Pg1441CurrentColdPreparation','Pg1450CurrentColdPreparation'),
                    ('pg1441-current-cold-prepared-v1','pg1452-current-cold-prepared-v1'),
                    ('PG1441_REFS_','PG1452_REFS_')]:
        if old not in raw:raise ValueError('explicit corrected observer binding absent')
        raw=raw.replace(old,new)
    compile(raw,'<new corrected observer>','exec');return raw


def qualified_handoff():
    value=json.loads((W/'pg1449-current-cold-owner-handoff-v1/manifest.safe.json').read_bytes())
    if not(value['actualExit']==0 and value['guest']['parentGone'] and value['guest']['allScopesClosedNormally']
           and value['guest']['reservationDurable'] and value['guest']['signalAttempted']
           and not value['guest']['oldJavaNormalClose']):
        raise ValueError('full current handoff required')


def compile_tools():
    qualified_handoff()
    body=inspect.getsource(compiler.main)
    for old,new in [('Pg1441CurrentColdPreparation','Pg1450CurrentColdPreparation'),
                    ('pg1441_current_cold_refs.py','pg1450_current_cold_refs.py'),
                    ('pg1441_current_cold_sources_test.py','pg1450_current_cold_retry_test.py'),
                    ('PG1442-current-cold-compile-v1','PG1450-current-cold-compile-v1'),
                    ('pg1442-current-cold-frozen-v1.safe.json','pg1450-current-cold-frozen-v1.safe.json')]:
        if old not in body:raise ValueError('compiler replacement absent')
        body=body.replace(old,new)
    ns=dict(compiler.__dict__,OUT=TOOLS,java=java,observer=observer)
    exec(compile(body,'<new-only current compiler>','exec'),ns)
    return ns['main']()


def stage_tools():
    qualified_handoff()
    body=inspect.getsource(stage.main)
    for old,new in [('pg1444-current-cold-frozen-v2.safe.json','pg1450-current-cold-frozen-v1.safe.json'),
                    ('pg1446','pg1451'),('PG1446','PG1451'),
                    ('pg1441-current-cold-tools-v1','pg1450-current-cold-tools-v1')]:
        if old not in body:raise ValueError('stage replacement absent')
        body=body.replace(old,new)
    ns=dict(stage.__dict__,OUT=W/'pg1451-current-cold-stage-v1',TOOLS=TOOLS)
    exec(compile(body,'<new-only corrected guest stage>','exec'),ns)
    ns['main']();return 0


def prepare():
    qualified_handoff()
    assert not subprocess.check_output(['git','status','--porcelain'])
    frozen=json.loads(FROZEN.read_bytes());stage_result=json.loads((W/'pg1451-current-cold-stage-v1/manifest.safe.json').read_bytes())
    assert frozen['actualExit']==0 and stage_result['actualExit']==0 and stage_result['frozenOperatorSource']==frozen['operatorSource']
    os.umask(0o077);out=W/'pg1452-current-cold-owned-prepare-v1';out.mkdir(mode=0o700)
    code=r'''import pathlib,hashlib,os,json
require=lambda x:None if x else (_ for _ in ()).throw(ValueError('fresh current prepare precondition refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
require(not pathlib.Path('/proc/3323').exists())
tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1450-current-cold-tools-v1')
require(set(os.listdir(tools))==set(HASHES)|{'payload-sha256.json'})
for name,digest in HASHES.items():require(hashlib.sha256((tools/name).read_bytes()).hexdigest()==digest)
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1452-current-cold-prepared-v1');require(not save.exists())
release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
cp=':'.join(map(str,[tools,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*']))
os.execv('/opt/jdk-25.0.4/bin/java',['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1450CurrentColdPreparation','prepare'])
'''
    code='HASHES='+repr(frozen['fileHashes'])+'\n'+code
    begin={'run':'PG1452-current-cold-owned-prepare-v1','productionSource':frozen['productionSource'],'frozenOperatorSource':frozen['operatorSource'],'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    with(out/'begin.safe.json').open('x')as f:json.dump(begin,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with(out/'observer.private.log').open('xb')as f:
        r=subprocess.run(stage.SSH+['sudo','-n','python3','-'],input=code.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    result=dict(begin,actualExit=r.returncode,logSha256=compiler.sha(out/'observer.private.log'))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True));return r.returncode


if __name__=='__main__':
    if sys.argv[1:] not in [['compile'],['stage'],['prepare']]:raise SystemExit('fixed compile/stage/prepare required')
    raise SystemExit({'compile':compile_tools,'stage':stage_tools,'prepare':prepare}[sys.argv[1]]())
