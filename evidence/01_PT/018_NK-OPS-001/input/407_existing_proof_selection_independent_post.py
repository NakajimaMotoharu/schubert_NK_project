"""Independent finite metadata correction and selection-mistake negative checks; no Product run."""
from pathlib import Path
import datetime,json,hashlib,ast,copy,collections,shutil
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'evidence/PG23350-existing-proof-selection-gate-v1';O=B/'evidence/PG23352-existing-proof-selection-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=load(I/'manifest.json');assert not O.exists() and m['actualExit']==0 and m['rows']==932 and m['productTestsExecuted']==0
for n,h in m['files'].items():assert sha(I/n)==h
matrix=Path(m['matrix']['path']);assert sha(matrix)==m['matrix']['sha256'];orig=load(matrix)['rows'];rows=load(I/'selection-rows.json');assert len(rows)==len(orig)==932 and {v['path'] for v in rows}=={v['path'] for v in orig};sources={v['path']:v for v in orig};counts=collections.Counter(v['evidenceStatus'] for v in orig);assert dict(counts)=={'NOT_IN_CURRENT_MEASUREMENT_REGISTRY':282,'NATURAL_ZERO_BRANCH':213,'FOUR100':334,'PARTIAL':80,'NO_CODE':23}
for row in rows:
 old=sources[row['path']];assert old['sha256']==row['originalSourceSha256'] and old['evidenceStatus']==row['originalStatus'];d=row['decision'];assert row['automaticUnitAllowed'] is False and row['newSourceAccepted'] is False
 if Path(row['path']).name in {'TemporaryInfrastructureException.java','FingerprintKeyRing.java','ResponseSnapshotCodec.java','WebStartupException.java'}:assert d.startswith('HOLD_')
 elif not row['sourceUnchanged']:assert d.startswith('SOURCE_CHANGE_')
 elif old['evidenceStatus'] in {'FOUR100','NATURAL_ZERO_BRANCH'}:assert d.startswith('EXISTING_COUNTER_')
 elif old['evidenceStatus']=='NO_CODE':assert d.startswith('NO_CODE_')
 elif row['namedCandidate'] or row['pending']:assert d.startswith('EXISTING_NAMED_')
 elif old['evidenceStatus']=='PARTIAL':assert d.startswith('PARTIAL_')
 else:assert old['evidenceStatus']=='NOT_IN_CURRENT_MEASUREMENT_REGISTRY' and d.startswith('UNBOUND_')
confirmed=load(I/'confirmed-existing-three.json');assert len(confirmed)==3;post=load(R/m['currentQualification']['path']);assert sha(R/m['currentQualification']['path'])==m['currentQualification']['sha256'];assert post['tests']==4 and post['newUniqueTests']==0
for v in confirmed:
 p=R/v['historicalProof']['path'];assert sha(p)==v['historicalProof']['sha256'];old=load(p);q=sources[v['path']]['qualifiedUnitProof'];assert q['postSha256']==sha(p);assert old['actualExit']==0 and v['sourceSha256']==sources[v['path']]['sha256']==sha(R/v['path']);f=v['physical'];assert old['physicalClasses'][f]==post['physical'][f]==v['physicalSha256'];assert old['fullSourceUnits'][f]['totals']==v['historicalCounters'] and all(x['missed']==0 for x in v['historicalCounters'].values());assert v['newSourceProofDelta']==0 and v['currentRequalifiedWholeProof']==1
# Pure metadata input-validation negatives: the predicate is extracted from the current declared
# selection tool, not any Product source or held Test. No fixture/Product execution is introduced.
tool=R/m['tool']['path'];assert sha(tool)==m['tool']['sha256'];tree=ast.parse(tool.read_text());f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='choose');ns={};exec(compile(ast.Module(body=[f],type_ignores=[]),str(tool),'exec'),ns);choose=ns['choose'];base=dict(sha256='a'*64,evidenceStatus='FOUR100');tests=[(base,'a'*64,{},'EXISTING_COUNTER_'),(base,'b'*64,{},'SOURCE_CHANGE_'),(dict(base,evidenceStatus='NOT_IN_CURRENT_MEASUREMENT_REGISTRY'),'a'*64,{},'UNBOUND_'),(dict(base,evidenceStatus='PARTIAL'),'a'*64,{},'PARTIAL_'),(dict(base,evidenceStatus='NOT_IN_CURRENT_MEASUREMENT_REGISTRY'),'a'*64,dict(pending=True),'EXISTING_NAMED_'),(base,'a'*64,dict(held=True),'HOLD_')]
for row,h,kw,prefix in tests:assert choose(row,h,**kw).startswith(prefix)
assert not any('ALLOW_UNIT' in choose(row,h,**kw) or 'NEW_PROOF' in choose(row,h,**kw) for row,h,kw,_ in tests)
O.mkdir();files={}
for n in m['files']:
 shutil.copyfile(I/n,O/n);files[n]=sha(O/n)
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['currentQualification'],reviewed932SelectionRows=932,confirmedExistingThree=confirmed,correctedNewSourceQualification=0,currentRunWholeSourceRequalifications=3,originalProductTests=4,newUniqueDelta=0,metadataNegativeChecks=6,productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,allCurrent93Qualified=False,effortRate=None,newAcceptance=0,formalUpdated=False,whole451Accepted=False,originalEventAndCostUnmodified=True,correctionOfEvent='PGPT-20261008-4311',originalManifest=dict(path=str((I/'manifest.json').relative_to(R)),sha256=sha(I/'manifest.json')),files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,correctNewSource=0,requalifiedThree=3,negative6=6,productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
