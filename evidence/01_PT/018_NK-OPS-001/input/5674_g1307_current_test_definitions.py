import hashlib,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree as ET
root=Path('evidence/01_PT')
ops=root/'018_NK-OPS-001/evidence'
def mr(n):
    return next(root.glob(f'*/evidence/PG{n}*/manifest.json'))
def load(p):
    return json.loads(p.read_bytes())
def pin(p):
    return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def git(*args):
    return subprocess.check_output(['git',*args])
base='b1e9d6eeac0cd60cb3e999c9c7b7c50c4e662f8f'
head=git('rev-parse','HEAD').decode().strip()
cases={
 'AnimationListCountBoundaryTest':(41182, ['PT-WEB-SCR009-COUNT-001']),
 'MusicCategoryCountBoundaryTest':(41178, ['PT-WEB-SCR011-COUNT-001']),
 'MusicSectionCountBoundaryTest':(41176, ['PT-WEB-SCR012-COUNT-001']),
 'MusicTrackCountBoundaryTest':(41188, ['PT-WEB-SCR013-COUNT-001']),
 'UserListLastPageCountTest':(41226, ['PT-WEB-SCR015-COUNT-001']),
 'JdbcFailureGraphOrderTest':(41230, ['PT-OPS-JDBCGRAPH007','PT-OPS-JDBCGRAPH006','PT-OPS-JDBCGRAPH008']),
 'FieldCodecTest':(41304, ['PT-PRO-002-N03']),
 'StorageFailureGraphTest':(41294, ['PT-OPS-STGRAPH-GENERIC-002','PT-OPS-STGRAPH-GENERIC-001']),
 'WebLogPayloadCodecTest':(41354, ['PT-WEB-WEBLOG-OWN002','PT-WEB-WEBLOG-OWN003']),
 'ExceptionValueContractTest':(41260, ['PT-MED-FAILURE-NAME-001']),
 'HttpByteRangeDecimalLimitTest':(41260, ['PT-MED-RANGE-BOUND-001']),
 'HttpByteRangeLongBoundaryTest':(41260, ['PT-MED-RANGE-LONG-001']),
 'HttpByteRangeUnitTokenTest':(41260, ['PT-MED-RANGE-UNIT-002','PT-MED-RANGE-UNIT-001']),
 'MediaRangePortTest':(41260, ['PT-MED-PORT009','PT-MED-PORT011',None,'PT-MED-PORT010']),
 'OutboxRetainedValueContractTest':(41404, ['PT-OUTBOX-COPY002','PT-OUTBOX-COPY001']),
 'ArtifactComparatorTest':(41344, ['PT-CHR-DEF081','PT-CHR-DEF082','PT-CHR-DEF080','PT-CHR-DEF079']),
}
inventory=git('diff','--name-only',base,head,'--','src','program/characterization').decode().splitlines()
closure={Path(p).stem:Path(p) for p in inventory if Path(p).stem in cases and ('/src/test/' in p or '/tests/java/' in p)}
assert set(closure)==set(cases)
annotations=re.compile(r'@Test\b[^\n]*(?:\s+@[^\n]+)*\s+(?:final\s+)?void\s+(\w+)\s*\(')
def check_xml(path,cl,method):
    tree=ET.parse(path).getroot()
    rows=[r for r in tree.iter('testcase') if r.get('name').removesuffix('()')==method and r.get('classname').rsplit('.',1)[-1]==cl]
    assert len(rows)==1 and all(rows[0].find(n) is None for n in ('failure','error','skipped')), (path,method)
def nested_path(value,pattern):
    if isinstance(value,dict):
        path=value.get('path')
        if isinstance(path,str) and path.endswith(pattern) and 'sha256' in value:
            yield value
        for row in value.values():
            yield from nested_path(row,pattern)
    if isinstance(value,list):
        for row in value:yield from nested_path(row,pattern)
rows=[]
for test_class,input_file in sorted(closure.items()):
    current=input_file.read_text()
    original=subprocess.run(['git','show',f'{base}:{input_file}'],check=False,capture_output=True,text=True)
    assert original.returncode in (0,128)
    current_added=sorted(set(annotations.findall(current))-set(annotations.findall(original.stdout)))
    pg,ids=cases[test_class]
    assert len(current_added)==len(ids),(test_class,current_added,ids)
    manifest=mr(pg)
    data=load(manifest)
    assert data.get('actualExit',data.get('executionExit'))==0
    known_xml=manifest.with_name('jupiter.xml')
    proof_names=[]
    if known_xml.exists():
        proof_names=[known_xml]
    elif pg in (41188,41354,41344):
        proof_names=[Path(ref['path']) for ref in nested_path(data,'TEST-junit-jupiter.xml')]
        assert len(set(proof_names))==1,pg
        assert any(pin(proof_names[0])==ref for ref in nested_path(data,'TEST-junit-jupiter.xml'))
    elif pg in (41176,41178):
        proof_names=[Path(data['case']['path'])]
        assert pin(proof_names[0])==data['case']
    elif pg in (41182,41294,41304):
        proof_names=[manifest.with_name('cases.json') if pg==41304 else manifest]
    else:
        raise ValueError(pg)
    assert proof_names
    observed=proof_names[0]
    original_source=data.get('fixedFixtureCommit') if pg==41230 else data.get('testSource',data.get('source'))
    if isinstance(original_source,dict):
        assert original_source['path']==str(input_file) and original_source['sha256']==pin(input_file)['sha256']
    else:
        assert isinstance(original_source,str)
        assert git('show',f'{original_source}:{input_file}')==input_file.read_bytes(),(test_class,original_source)
    for method,identifier in zip(current_added,ids,strict=True):
        if observed.suffix=='.xml':
            check_xml(observed,test_class,method)
        else:
            assert method in observed.read_text(),(pg,method)
        k='FIXTURE_ONLY' if identifier is None else ('CHARACTERIZATION_TOOL' if pg==41344 else 'PRODUCT')
        rows.append(dict(PT=identifier,kind=k,testClass=test_class,method=method,fixture=pin(input_file),
             originalSource=original_source,originalQualification=pin(manifest),recordedOutcome=pin(observed),
             formalAcceptance=False,countsAsNewProduct=k=='PRODUCT'))
ids=[r['PT'] for r in rows if r['PT']]
assert len(ids)==len(set(ids))==27
counts={k:sum(r['kind']==k for r in rows) for k in ('FIXTURE_ONLY','CHARACTERIZATION_TOOL','PRODUCT')}
assert counts==dict(FIXTURE_ONLY=1,CHARACTERIZATION_TOOL=4,PRODUCT=23)
out=ops/'PG41430-g1307-current-new-test-ids-v1'
out.mkdir()
report=dict(run=out.name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),testedSource=head,
    comparisonBase=base,productionCore='2611e1acbd57955d591d52e5348999ea293e068d',newTestDeclarations=len(rows),
    independentRecordedTestCategories=counts,trace=rows,nativeCaseReplays=0,productTestsExecuted=0,
    sourceScopeDiffOnly=True,formalDelta=0,projectCoverageMerged=False,whole451=False)
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(counts,len(rows))
