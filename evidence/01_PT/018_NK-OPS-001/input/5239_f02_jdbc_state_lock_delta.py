"""Refresh only the two changed Bootstrap types and trace the new cross-thread test."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
import gzip
import runpy
import subprocess

HERE=Path(__file__)
Q=runpy.run_path(str(HERE.with_name('5223_f02_cleanup_fixed_statement_edges.py')))
E,H,G=map(Q.get,('E','H','G'))
read,ref,write,verified=map(Q.get,('read','ref','write','verified'))
FULL='dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSource'
MAIN='src/schubert-nk-bootstrap/src/main/java/'+FULL.replace('.','/')+'.java'
TEST=MAIN.replace('/main/java/','/test/java/').replace('ServiceDatabaseSource.java','ServiceDatabaseSourcePortTest.java')
NEW_CASE='dbSource016ConnectorFailureReleasesTheStateLockForAnotherThread'
DOC=Path('evidence/01_PT/018_NK-OPS-001/4697_ServiceDatabaseSource同一lockの単体仕様.md')
PHY=tuple((name,'bootstrap',name.replace('.','/')+'.class') for name in (FULL,FULL+'$StateAction'))


def edge_history(proof):
    _,_,scope,older,sdk=map(verified,proof['priorProofs'])
    rows=Q['combined_original'](older['f02PhysicalEdges'],scope)
    cmd=verified(proof['command'])
    path=Path(cmd['stdout']['path'])
    assert ref(path)==cmd['stdout']
    data=gzip.decompress(path.read_bytes())
    assert G['sha'](data)==cmd['originalStdoutSha256']
    old_names={proof['removedPhysical'],proof['changedPhysical']}
    return [(a,b,c) for a,b,c in rows if a not in old_names]+G['edges'](data.decode()),sdk


def observe(m,out):
    workspace=Path(m['cwd'])
    assert workspace.parent==Path('../pgpt-runs/PG379').resolve()
    exec_file=Path('../toolchain/jdk-25.0.4/bin/jdeps').resolve()
    assert G['sha'](exec_file.with_name('java').read_bytes())==m['tools']['javaSha256']
    paths=[workspace/f'src/schubert-nk-{module}/target/classes'/path for _,module,path in PHY]
    fixtures=[ref(file) for file in paths]
    assert all(pin['sha256']==m['physicalClassHashes'][module][path] and file.resolve()==file
               for file,pin,(_,module,path) in zip(paths,fixtures,PHY,strict=True))
    args=[str(exec_file),'-verbose:class','-filter:none','--ignore-missing-deps',*map(str,paths)]
    start=datetime.now(timezone.utc).isoformat()
    actual=subprocess.run(args,capture_output=True,timeout=30)
    assert actual.returncode==0 and not actual.stderr
    with (out/'jdeps.stdout.gz').open('xb') as f:f.write(gzip.compress(actual.stdout,mtime=0))
    receipt=dict(actualExit=0,command=args,startedAtUTC=start,inputs=fixtures,sdk=ref(exec_file),
                 stdout=ref(out/'jdeps.stdout.gz'),originalStdoutSha256=G['sha'](actual.stdout),
                 terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(out/'jdeps-command.json',receipt)
    rows=G['edges'](actual.stdout.decode())
    assert {name for name,_,_ in rows}=={row[0] for row in PHY}
    return rows,ref(out/'jdeps-command.json')


def trace(post,head):
    unit=verified(post['unit'])
    xml=Path(post['actualWholeCases']['path'])
    assert ref(xml)==post['actualWholeCases']
    original=ET.parse(xml).getroot().findall('testcase')
    [case]=[r for r in original if r.get('name')==NEW_CASE+'()']
    assert case.get('classname')==FULL+'PortTest'
    assert not any(c.tag in ('error','failure','skipped') for c in case)
    for path in (MAIN,TEST):
        assert G['git']('show',f'{head}:{path}')==G['git']('show',f'{unit["unitSource"]}:{path}')==Path(path).read_bytes()
    assert 'PT-OPS-DBSRCPORT-016' in DOC.read_text() and NEW_CASE in Path(TEST).read_text()
    registry=Path('documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')
    [owner]=[r for r in read(registry)['artifacts'] if r['path']==MAIN]
    assert owner['class'].replace('/','.')==FULL
    return dict(id='PT-OPS-DBSRCPORT-016',member=NEW_CASE,test=ref(Path(TEST)),source=ref(Path(MAIN)),
                spec=ref(DOC),caseXml=ref(xml),latestUnitSource=unit['unitSource'],singleExec=post['singleExec'],
                classCRC=post['classes'][FULL.replace('.','/')]['crc'],owner=owner['owner'],
                costOwner=owner['costOwner'],recordedMonitor='PG-D-1189',linkedBug='BUG-3312',g08ReferenceCostPp=0)


def main():
    start=read(next(H.glob('517_*')))
    v=start['values']
    head=v['source']
    assert G['git']('rev-parse','HEAD').decode().strip()==head
    assert G['git']('rev-parse','origin/dev-foundation').decode().strip()==head
    prior,build,post=map(verified,v['oracleReferences'])
    assert build['sourceCore']==post['source']==v['productionCoreMain']
    old=verified(build['baselineCompile'])
    assert old['sourceCore']==prior['source'] and build['actualExit']==0 and post['tests']==32
    keys=G['class_owners']
    old_index,new_index=[keys(x['physicalClassHashes']) for x in (old,build)]
    assert len(old_index)==1101 and len(new_index)==1102
    assert new_index.keys()-old_index.keys()=={FULL+'$StateAction'}
    assert old_index.keys()<=new_index.keys()
    old_same=sum(build['physicalClassHashes'][module].get(name)==d
                 for module,paths in old['physicalClassHashes'].items() for name,d in paths.items())
    assert old_same==1100
    original,sdk=edge_history(prior)
    assert G['analyze'](original,old_index)==prior['after']
    out=E/v['run']
    rows,cmd=observe(build,out)
    updated=[r for r in original if r[0]!=FULL]+rows
    current=G['analyze'](updated,new_index)
    assert current['edges']==prior['after']['edges']
    assert len(set(updated))==len(updated) and not current['internalUnresolved']
    assert Q['external'](original)==Q['external'](updated) and len(Q['external'](updated))==sdk['currentReferencePairs']==385
    assert any(a.endswith('.StorageIoException') and b=='java.sql.SQLException' for a,b,_ in updated)
    before_set={r for r in original if r[0]==FULL}
    after_set=set(rows)
    value=dict(actualExit=0,source=build['sourceCore'],groupStart=start['eventId'],
        currentTypedEdges=current,fromTypedEdges=prior['after'],unchangedPhysical=1100,
        changedOldPhysical=1,addedNoCodePhysical=1,checked=cmd,
        changedRowsAdded=sorted(after_set-before_set),changedRowsRemoved=sorted(before_set-after_set),
        exactExternal385=True,actualHostTests=0,newCoverage=0,productTestReplay0=True,
        storageSqlBlockOpen=True,wholeSixBoundaryAccepted=False,whole451Accepted=False,newAcceptance=0,
        reusableRefs=v['oracleReferences'],trace=trace(post,head),verifier=ref(HERE),terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(out/'manifest.json',value)
    print(ref(out/'manifest.json'),current)


if __name__=='__main__':
    main()
