import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from zipfile import ZipFile
from class_source_file import source_file
base=Path('documents/400_PGPT/470_PMO')
ops=Path('evidence/01_PT/018_NK-OPS-001/evidence')
def load(path):
    return json.loads(path.read_bytes())
def pin(path):
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def git(*args):
    return subprocess.check_output(['git',*args])
old_path=next(ops.glob('PG41304*/manifest.json'))
old=load(old_path)
binding_path=next(ops.glob('PG41308*/manifest.json'))
binding=load(binding_path)
jar_receipt=next(ops.glob('PG41306*/manifest.json'))
retained=load(jar_receipt)['retained']['localJar.jar']
jar=Path(retained['path'])
assert pin(jar)==retained and old['localJar']['sha256']==retained['sha256']
head=git('rev-parse','HEAD').decode().strip()
core='007b96d8be7c10e265b5a12d01231013ae9e0acd'
module=Path('src/schubert-nk-protocol')
assert not git('diff','--name-only',old['source'],head,'--',str(module),'pom.xml','tools/quality/static')
tags=('LINE','METHOD','CLASS','BRANCH','INSTRUCTION')
physical={}
raw_path=Path(old['evidence'][0]['path'])
cases_path=Path(old['evidence'][1]['path'])
assert [pin(p) for p in (raw_path,cases_path)]==old['evidence']
for line in raw_path.read_text().splitlines():
    part=line.split('\t')
    if part[0]!='CLASS':
        continue
    binary=part[1]
    assert binary not in physical
    counters={}
    for unit in part[6:]:
        tag,missed,covered=unit.split(':')
        counters[tag]=dict(missed=int(missed),covered=int(covered))
    assert all(counters[key]['missed']==0 for key in tags)
    physical[binary]=dict(crc64=part[2],observed=part[3]=='true',counters=counters)
assert len(physical)==old['jarPhysicalCount']==176
assert sum(row['observed'] for row in physical.values())==old['execClasses']==162
assert old['singleSession'] and not old['execMerged'] and old['actualExit']==old['notRun']==old['failures']==old['errors']==old['skipped']==0
for tag in tags:
    assert sum(row['counters'][tag]['covered'] for row in physical.values())==old['coverageRaw'][tag]['covered']
with ZipFile(jar) as f:
    entries=[n for n in f.namelist() if n.endswith('.class')]
    assert len(entries)==len(set(entries))==len(physical) and {n.removesuffix('.class') for n in entries}==set(physical)
    for name in entries:
        row=physical[name.removesuffix('.class')]
        source=module/'src/main/java'/Path(name).parent/source_file(f.read(name))
        data=git('show',f'{core}:{source}')
        assert data==source.read_bytes()
        row['exactSource']=pin(source)
master_path=next(base.glob('481_*.json'))
snapshot_path=next(base.glob('486_*.json'))
original=load(master_path)
snapshot=load(snapshot_path)
roles=('WBS-P001-01','WBS-P001-02','WBS-P002-01')
case_roster=load(cases_path)
assert len(case_roster)==old['ordinaryTests']==171 and old['suites']==39 and {v['outcome'] for v in case_roster}=={'PASS'}
assert len({(v['className'],v['method']) for v in case_roster})==len(case_roster)
def selected_tests(scope):
    packages={
       'WBS-P001-01':('header.',),
       'WBS-P001-02':('layout.Layout','layout.PayloadTypeCatalog'),
       'WBS-P002-01':('codec.FieldCodec', 'codec.TypedUnsigned', 'layout.semantic.'),
    }
    prefix='dev.codex.schubert.nk.protocol.'
    return [r for r in case_roster if r['className'].startswith(tuple(prefix+name for name in packages[scope]))]
rows=[]
for id in roles:
    authority=next(t for t in original['tasks'] if t['id']==id)
    status=next(t for t in snapshot['rows'] if t['id']==id)['acceptance']
    assert status==authority['acceptance']
    permission='RECHECK_REQUIRED' if id==roles[-1] else 'ACCEPTED'
    assert status['status']==permission
    owned=set(authority['ownedArtifacts'])
    matched={name:r for name,r in physical.items() if r['exactSource']['path'] in owned}
    assert owned=={r['exactSource']['path'] for r in matched.values()}
    totals={tag:sum(row['counters'][tag]['covered'] for row in matched.values()) for tag in tags}
    supported=selected_tests(id)
    assert supported
    if id==roles[-1]:
        assert authority['dependencies']==list(roles[:2])
        assert any(row['method']=='numericDecodeValidatesEveryByteBeforeAccumulatingTheValue' for row in supported)
    rows.append(dict(wbsId=id,priorStatus=permission,historicalAcceptanceSource=status['source'],
        ownedMainFiles=len(owned),sameRunPhysicalClasses=len(matched),codeBearingClasses=sum(row['observed'] for row in matched.values()),
        rawCovered=totals,rawMissed=dict.fromkeys(tags,0),testSamples=supported,perClass=matched,
        currentFormalAcceptance=False))
out=ops/'PG41394-protocol-three-scope-current-recheck-v1'
out.mkdir()
value=dict(run=out.name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    source=head,productionCore=core,qualifiedProtocolSource=old['source'],previous=pin(binding_path),
    currentProtocol=pin(old_path),exactJar=retained,physicalCount=176,sourceIdentityVerified=True,originalRoster=pin(cases_path),
    originalOrdinaryPt=171,originalSuites=39,originalExecMerged=False,whole451=False,actualChr=0,
    wbsOriginal=pin(master_path),currentState=pin(snapshot_path),scopeRows=rows,
    formalDelta=0,restoredOriginalLeaf=0,newTests=0,priorTestsRerun=0,noCoverageUnion=True,
    stillRequired=['P001-01 / P001-02 累積正式判断と当sourceの終了依存','P002-01 独立要求・test traceの現行全接続','新source全451と影響CHR'])
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print([(v['wbsId'],v['ownedMainFiles'],v['sameRunPhysicalClasses'],v['rawCovered'],len(v['testSamples'])) for v in rows])
