"""Freeze the current admitted four-module Main build and verify the single source delta."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil

HERE=Path(__file__)
R=runpy.run_path(str(HERE.with_name('5227_p020_definition_uniqueness_run.py')))
E,D=R['E'],R['D']
ref,read,save,git=[R[k] for k in ('ref','read','save','git')]
START=next(D.glob('515_*'))
OUT=E/'PG39862-service-db-state-lock-four-main-v1'
WORK=Path.cwd().parent/'pgpt-runs/PG379'/OUT.name.lower()
MAIN='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseSource.java'
PACKAGE='dev/codex/schubert/nk/api/bootstrap/'
MAIN_LEAF=PACKAGE+'ServiceDatabaseSource'
MODS=('protocol','storage','bootstrap','batch')


def main():
    start=read(START)
    old_head=git('rev-parse','HEAD').decode().strip()
    core=git('rev-parse','HEAD^').decode().strip()
    assert git('diff','--name-only',start['values']['productionCoreMain'],core,'--','src').decode().splitlines()==[MAIN]
    old_pin=start['values']['oracleReferences'][1]
    old_path=Path(old_pin['path'])
    assert ref(old_path)==old_pin
    old=read(old_path)
    assert old['sourceCore']==start['values']['productionCoreMain'] and old['actualExit']==0
    sources=old['sourceInputs']
    assert len(sources)==490 and old['mainCounts']==dict(protocol=169,storage=25,bootstrap=88,batch=200)
    inputs={name:git('show',f'{core}:{name}') for name in sources}
    assert all(Path(name).read_bytes()==raw for name,raw in inputs.items())
    pins={name:hashlib.sha256(raw).hexdigest() for name,raw in inputs.items()}
    assert {name for name,h in pins.items() if h!=sources[name]}=={MAIN}
    assert shutil.disk_usage(Path.cwd()).free>=1024**3
    assert not OUT.exists() and not WORK.exists()
    OUT.mkdir()
    WORK.mkdir(mode=0o700)
    for name,data in inputs.items():
        item=WORK/name
        item.parent.mkdir(parents=True,exist_ok=True)
        item.write_bytes(data)
    orig=old['command']
    assert orig[-1]=='compile' and orig[-2]=='-am'
    save(OUT/'begin.json',dict(compiledCore=core,expectedUnitSource=old_head,inputs=pins,
        priorCompile=old_pin,argv=orig,classfilesOnly=True,productTestsExecuted=0))
    result=R['step']('maven',orig,WORK,OUT,180)
    log=Path(result['log']['path'])
    archive=log.with_suffix('.log.gz')
    archive.write_bytes(gzip.compress(log.read_bytes(),mtime=0))
    assert hashlib.sha256(gzip.decompress(archive.read_bytes())).hexdigest()==result['log']['sha256']
    physical={mod:R['physical'](WORK/f'src/schubert-nk-{mod}/target/classes') for mod in MODS}
    deltas={}
    for mod,m in physical.items():
        p=old['physicalClassHashes'][mod]
        deltas[mod]=dict(added=sorted(m.keys()-p.keys()),removed=sorted(p.keys()-m.keys()),
              changed=sorted(k for k in m.keys()&p.keys() if m[k]!=p[k]))
    assert all(ref(WORK/name)['sha256']==sha and ref(Path(name))['sha256']==sha for name,sha in pins.items())
    if result['actualExit']==0:
        assert deltas['bootstrap']==dict(added=[MAIN_LEAF+'$StateAction.class'],removed=[],changed=[MAIN_LEAF+'.class'])
        assert all(not any(row.values()) for mod,row in deltas.items() if mod!='bootstrap')
        assert sum(map(len,physical.values()))==1102
    value=dict(actualExit=result['actualExit'],sourceCore=core,unitSource=old_head,cwd=str(WORK),
        sourceInputs=pins,inputHashesReverified=True,baselineSource=old['sourceCore'],baselineCompile=old_pin,
        physicalClassHashes=physical,deltas=deltas,command=orig,tools=old['tools'],
        mainCounts=old['mainCounts'],changedSources=[MAIN],terminalAtUTC=R['utc'](),
        productTestsExecuted=0,logArchive=ref(archive),maven=result,verifier=ref(HERE))
    save(OUT/'manifest.json',value)
    print(result['actualExit'],core,{k:len(v) for k,v in physical.items()},deltas)
    return result['actualExit']


if __name__=='__main__':
    raise SystemExit(main())
