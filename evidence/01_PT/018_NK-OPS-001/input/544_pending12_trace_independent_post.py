"""Independently join original XML/input pins, owner decisions and exact485 delta; no target run."""
from pathlib import Path
from collections import Counter
import copy,datetime,hashlib,json,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001'
P=B/'evidence/PG23836-pending12-trace-registration-v1';O=B/'evidence/PG23838-pending12-trace-independent-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='9bb0a15ccaf88696423ef084af27172595e23c34b581943cb7e9399d93a0c87b'
assert m['actualExit']==m['newAcceptance']==0 and m['formalUpdated'] is False and m['effortRate'] is None
for name,h in m['files'].items():assert sha(P/name)==h
cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256']
supp=load(R/m['supplement']['path']);assert sha(R/m['supplement']['path'])==m['supplement']['sha256']
normal=Path(cfg['normalManifestPath']);assert sha(normal)==cfg['normalManifestSha256'];normal=load(normal)
wp=R/m['wbsAfter']['path'];assert sha(wp)==m['wbsAfter']['sha256'];current=load(wp)
raw=subprocess.check_output(['git','show',m['observerHead']+':'+cfg['wbsBefore']['path']],cwd=R)
assert hashlib.sha256(raw).hexdigest()==cfg['wbsBefore']['sha256'];before=json.loads(raw)
beforeRows={v['path']:v for v in before['artifacts']};afterRows={v['path']:v for v in current['artifacts']}
assert len(beforeRows)==941 and len(afterRows)==942 and set(afterRows)-set(beforeRows)=={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebServiceMetricBinding.java'}
assert len(current['artifacts'])==len(afterRows)
# Verify all unrelated485 values/rows are unchanged, not merely selected counters.
oldOther={k:v for k,v in before.items() if k!='artifacts'}
newOther={k:v for k,v in current.items() if k not in ('artifacts',m['overlayKey'])};assert oldOther==newOther
for n,v in beforeRows.items():
 if n not in supp['ownerCorrections']:assert v==afterRows[n]
 else:
  assert {k:x for k,x in v.items() if k not in ('owner','costOwner','basis')}=={k:x for k,x in afterRows[n].items() if k not in ('owner','costOwner','basis')}
  assert afterRows[n]['owner']==afterRows[n]['costOwner']==supp['ownerCorrections'][n]
for n,owner in supp['ownerCorrections'].items():assert afterRows[n]['owner']==afterRows[n]['costOwner']==owner
rows=load(P/'source-trace.json');tests=load(P/'test-trace.json');groups=load(P/'proof-groups.json');originals={};expectedTests={};expectedCases=set();expectedXmlRefs={}
for path,pin in cfg['proofReferences'].items():
 q=R/path;assert sha(q)==pin;o=load(q);originals[path]=o
 assert o['actualExit']==0 and o['productionCoreMain']==normal['source'] and o['oldExecCombined'] is False and o['manualCoverageExclusions']==[]
 sources={n:h for n,h in o['inputHashes'].items() if '/src/test/java/' in n}; classes={n.split('/src/test/java/')[1][:-5].replace('/','.'):n for n in sources}
 localCases=[]; xmlRefs=[]
 for n,h in o['files'].items():
  if n.startswith('original-TEST-') and n.endswith('.xml'):
   assert '/' not in n;p=q.parent/n;assert sha(p)==h;root=E.parse(p).getroot()
   assert not root.findall('.//failure') and not root.findall('.//error') and not root.findall('.//skipped')
   ids=[]
   for v in root.findall('testcase'):
    cls=v.get('classname');method=v.get('name');assert cls in classes;identity=cls+'#'+method
    assert identity not in expectedCases;expectedCases.add(identity);localCases.append(identity);ids.append(identity)
   xmlRefs.append(dict(path=str(p.relative_to(R)),sha256=h,cases=ids))
 assert len(localCases)==o['tests'];expectedXmlRefs[path]=xmlRefs
 for n,h in sources.items():
  assert not any(x in n for x in ('RootFailedStart','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness'))
  assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',o['source']+':'+n],cwd=R)).hexdigest()
  cls=n.split('/src/test/java/')[1][:-5].replace('/','.');ids=[v for v in localCases if v.startswith(cls+'#')]
  if n not in expectedTests:expectedTests[n]=dict(sha256=h,caseIds=[],proofs=[])
  assert expectedTests[n]['sha256']==h;expectedTests[n]['caseIds']+=ids;expectedTests[n]['proofs'].append(path)
assert len(expectedTests)==12 and len(expectedCases)==96
def valid(rr,tt,gg):
 try:
  assert len(rr)==12 and len({v['mainPath'] for v in rr})==12 and set(tt)==set(expectedTests) and set(gg)==set(originals)
  for v in rr:
   n=v['mainPath'];assert n in afterRows and sha(R/n)==v['mainSha256']==normal['begin']['inputHashes'][n]
   assert v['canonicalOwner']==v['canonicalCostOwner']==afterRows[n]['owner']
   path=v['proof']['path'];o=originals[path];assert v['proof']['sha256']==cfg['proofReferences'][path]
   assert v['runSource']==o['source'] and v['productionCoreMain']==o['productionCoreMain']
   expected={k for k,x in o['sourceFilePhysicalClosure'].items() if x['sourceFile']==Path(n).name}
   assert expected==set(v['completeSourceFilePhysicalClasses']) and len(expected)==len(v['completeSourceFilePhysicalClasses'])
   assert v['classHashes']=={k:o['physical'][k] for k in expected} and v['classIds']=={k:o['classIds'][k] for k in expected}
   assert v['testSourcePaths']==sorted(gg[path]['testSourceHashes']) and v['executedCaseIds']==gg[path]['executedCaseIds']
   assert v['programDocuments']==supp['programDocuments'][path] and v['currentWholeSourceOrDependencyAcceptance'] is False and v['registeredComponentDelta'] is None
  assert {v['mainPath'] for v in rr}=={v['mainPath'] for v in cfg['pendingEntries']}
  for n,v in tt.items():
   expected=expectedTests[n];assert v['path']==n and v['sha256']==expected['sha256'] and v['executedCases']==expected['caseIds'] and v['proofs']==expected['proofs']
   assert v['entireTestClassAccepted'] is False
   assert v['role']==('SELECTED_TESTCASES_IN_ORIGINAL_RUN' if expected['caseIds'] else 'SOURCE_INPUT_WITH_NO_SELECTED_TESTCASES_NOT_TEST_PASS')
  for path,g in gg.items():
   o=originals[path];assert g['runSource']==o['source'] and g['coverage']==o['coverage'] and g['physical']==o['physical'] and g['sourceFilePhysicalClosure']==o['sourceFilePhysicalClosure']
   assert g['testSourceHashes']=={n:h for n,h in o['inputHashes'].items() if '/src/test/java/' in n}
   assert g['xmlReferences']==expectedXmlRefs[path] and sorted(g['executedCaseIds'])==sorted(v for ref in expectedXmlRefs[path] for v in ref['cases'])
   assert g['notRunDeclaredMethods']==o.get('notRunDeclaredMethods') and g['wholeOriginalTestAccepted']==o.get('wholeOriginal22Accepted')
   assert g['coverageScope']=='ORIGINAL_SINGLE_GROUP_UNSPLIT_DO_NOT_ADD_ACROSS_MAIN_ROWS_OR_RUNS' and g['oldExecCombined'] is False and g['whole451Accepted'] is False
   for ref in g['programDocuments']:assert sha(R/ref['path'])==ref['sha256']
  return True
 except (AssertionError,KeyError,TypeError):return False
assert valid(rows,tests,groups)
negatives=[]
for label,change in [('owner',lambda v:v[0].update(canonicalOwner='WBS-P019-01')),('cost-owner',lambda v:v[0].update(canonicalCostOwner='WBS-P019-01')),('missing-main',lambda v:v.pop()),('duplicate-main',lambda v:v.append(copy.deepcopy(v[0]))),('missing-physical',lambda v:v[0]['completeSourceFilePhysicalClasses'].pop()),('different-run',lambda v:v[0].update(runSource='0'*40))]:
 altered=copy.deepcopy(rows);change(altered);assert not valid(altered,tests,groups);negatives.append(label)
helper=next(n for n,v in expectedTests.items() if not v['caseIds']);altered=copy.deepcopy(tests);altered[helper]['role']='SELECTED_TESTCASES_IN_ORIGINAL_RUN';assert not valid(rows,altered,groups);negatives.append('helper-fake-pass')
altered=copy.deepcopy(tests);del altered[helper];assert not valid(rows,altered,groups);negatives.append('missing-helper-input')
altered=copy.deepcopy(groups);first=next(iter(altered));altered[first]['executedCaseIds'].append('unknown#fake()');assert not valid(rows,tests,altered);negatives.append('unexecuted-case-added')
assert sum(bool(v['caseIds']) for v in expectedTests.values())==11
overlay=current[m['overlayKey']];assert overlay['newTests']==overlay['newAcceptance']==0 and overlay['registeredComponentDelta'] is None
O.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['productionMain'],producer=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),wbsAfter=m['wbsAfter'],sourcePrograms=12,proofGroups=10,testSourceFiles=12,testSourcesWithSelectedCases=11,sourceInputsWithNoSelectedCases=1,existingExecutedCaseIds=96,newTestExecutions=0,canonicalOwnerChanges=3,missingMainRowsAdded=1,sharedBootstrapOwnerCorrections=2,unrelated941SnapshotValuesPreserved=True,independentMetadataNegativeChecks=len(negatives),negativeLabels=negatives,sourceMutation=False,productTestsExecuted=0,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,registeredComponentDelta=None,ptPassAdded=0,bugs=['BUG-2502','BUG-2503'],ykts=['YKT-2240','YKT-2241'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sources=12,proofs=10,testFiles=12,caseIds=96,sourceOnlyInput=1,negativeChecks=len(negatives),manifestSha256=sha(O/'manifest.json'))))
