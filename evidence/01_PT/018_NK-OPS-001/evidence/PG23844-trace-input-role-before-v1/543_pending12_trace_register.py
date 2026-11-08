"""Register existing own-port evidence, never replay code or combine original executions."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4]; B=R/'evidence/01_PT/018_NK-OPS-001'
C=B/'input/542_pending12_trace_scope.json'; D=B/'input/548_pending12_doc_owner_supplement.json'
O=B/'evidence/PG23836-pending12-trace-registration-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(C); supplement=load(D); assert not O.exists()
wp=R/cfg['wbsBefore']['path']; assert sha(wp)==cfg['wbsBefore']['sha256'];wb=load(wp)
before=load(B/'evidence/PG23840-pending-trace-owner-before-v1/manifest.json');assert before['beforeWbsSha256']==sha(wp)
normal=Path(cfg['normalManifestPath']);assert sha(normal)==cfg['normalManifestSha256'];nm=load(normal)
assert nm['actualExit']==0 and nm['source']==cfg['productionMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
indexp=B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json'
assert sha(indexp)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(indexp)
for ref in supplement['ownerDecisionDocuments']:
 p=R/ref['path'];assert sha(p)==ref['sha256']
assert 'WBS-P018-09' in (R/supplement['ownerDecisionDocuments'][0]['path']).read_text()
assert all('WBS-P018-05' in (R/ref['path']).read_text() for ref in supplement['ownerDecisionDocuments'][1:])
artifacts={v['path']:v for v in wb['artifacts']};assert len(artifacts)==len(wb['artifacts'])==941
groups={};tests={};allCases=set()
for path,pin in cfg['proofReferences'].items():
 p=R/path;assert p.is_relative_to(R/'evidence/01_PT') and p.name=='manifest.json' and sha(p)==pin
 m=load(p);assert type(m['actualExit']) is int and m['actualExit']==0 and m['newAcceptance']==0 and m['formalUpdated'] is False
 assert m['productionCoreMain']==cfg['productionMain'] and m['manualCoverageExclusions']==[] and m['oldExecCombined'] is False
 assert m['staticApplicable']==m['checkstyle']==m['heldFourInitializations']==0
 own={n:h for n,h in m['inputHashes'].items() if '/src/test/java/' in n};assert 1<=len(own)<=2
 classPaths={}
 for n,h in own.items():
  assert re.fullmatch(r'src/schubert-nk-(api|batch|web|bootstrap|storage)/src/test/java/[A-Za-z0-9_/$]+\.java',n)
  assert not any(v in n for v in ('RootFailedStart','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness'))
  q=R/n;assert sha(q)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()
  name=n.split('/src/test/java/',1)[1][:-5].replace('/','.')
  assert name not in classPaths;classPaths[name]=n
  if n in tests:assert tests[n]['sha256']==h
  else:tests[n]=dict(path=n,sha256=h,executedCases=[],proofs=[])
 xml=[];caseIds=[]
 for name,h in m['files'].items():
  if not (name.startswith('original-TEST-') and name.endswith('.xml')):continue
  assert '/' not in name and '..' not in name;q=p.parent/name;assert sha(q)==h
  root=E.parse(q).getroot();assert not any(root.findall('.//'+tag) for tag in ('failure','error','skipped'))
  ids=[]
  for row in root.findall('testcase'):
   cls=row.get('classname');method=row.get('name');assert cls in classPaths and re.fullmatch(r'[A-Za-z_$][\w$]*\(\)',method)
   identity=cls+'#'+method;assert identity not in allCases;allCases.add(identity);caseIds.append(identity);ids.append(identity)
   tests[classPaths[cls]]['executedCases'].append(identity)
  xml.append(dict(path=str(q.relative_to(R)),sha256=h,cases=ids))
 assert len(caseIds)==m['tests'] and len(xml)==3
 docs=supplement['programDocuments'][path];assert len(docs)>=2
 for ref in docs:assert sha(R/ref['path'])==ref['sha256']
 for n in own:tests[n]['proofs'].append(path)
 groups[path]=dict(manifestSha256=pin,runSource=m['source'],productionCoreMain=m['productionCoreMain'],testsExecuted=m['tests'],executedCaseIds=sorted(caseIds),testSourceHashes=own,xmlReferences=xml,programDocuments=docs,coverageScope='ORIGINAL_SINGLE_GROUP_UNSPLIT_DO_NOT_ADD_ACROSS_MAIN_ROWS_OR_RUNS',coverage=m['coverage'],sourceFilePhysicalClosure=m['sourceFilePhysicalClosure'],physical=m['physical'],classIds=m['classIds'],staticPreflight=m['staticPreflight'],wholeOriginalTestAccepted=m.get('wholeOriginal22Accepted'),notRunDeclaredMethods=m.get('notRunDeclaredMethods'),manualCoverageExclusions=[],oldExecCombined=False,whole451Accepted=False,newAcceptance=0)
assert len(groups)==10 and len(allCases)==96
rows=[];ownerChanges=[]
for pending in cfg['pendingEntries']:
 n=pending['mainPath'];assert '/src/main/java/' in n and n in nm['begin']['inputHashes']
 assert sha(R/n)==nm['begin']['inputHashes'][n]
 g=groups[pending['manifest']['path']]; main={k:v for k,v in g['sourceFilePhysicalClosure'].items() if v['sourceFile']==Path(n).name}
 expected={k for k,v in index.items() if v['path']==n};assert set(main)==expected and expected
 for k in expected:assert g['physical'][k]==index[k]['sha256'] and g['classIds'][k]==index[k]['crc64']
 previous=artifacts.get(n);owner=supplement['ownerCorrections'].get(n,previous['owner'] if previous else None)
 assert owner is not None
 if n in supplement['ownerCorrections']:
  assert previous==before['beforeRows'][n];ownerChanges.append(dict(path=n,before=previous,afterOwner=owner))
  if previous:
   previous['owner']=previous['costOwner']=owner;previous['basis']='PG23836: explicit current Program source responsibility and common bootstrap ownership; old row retained in PG23840 before snapshot.'
  else:
   module=n.split('/')[1].removeprefix('schubert-nk-');outer=next(k for k in expected if '$' not in k)
   previous=dict(path=n,kind='JAVA',module=module,**{'class':outer},owner=owner,costOwner=owner,basis='PG23836: missing Main added from explicit3752 WBS-P018-09; no acceptance inferred.',sha256=sha(R/n),acceptance='UNASSESSED',counterApplicability='EXECUTABLE_OR_MEASUREMENT_REQUIRED')
   wb['artifacts'].append(previous);artifacts[n]=previous
 rows.append(dict(mainPath=n,mainSha256=sha(R/n),canonicalOwner=owner,canonicalCostOwner=owner,legacyOwner=(before['beforeRows'][n] or {}).get('owner') if n in before['beforeRows'] else owner,proof=pending['manifest'],runSource=g['runSource'],productionCoreMain=g['productionCoreMain'],completeSourceFilePhysicalClasses=sorted(expected),classHashes={k:g['physical'][k] for k in expected},classIds={k:g['classIds'][k] for k in expected},testSourcePaths=sorted(g['testSourceHashes']),executedCaseIds=sorted(g['executedCaseIds']),programDocuments=g['programDocuments'],coverageRefScope='PROOF_GROUP_UNSPLIT',currentWholeSourceOrDependencyAcceptance=False,registeredComponentDelta=None,whole451Accepted=False))
assert len(rows)==12 and len(ownerChanges)==3 and len(wb['artifacts'])==942
assert all(t['executedCases'] for t in tests.values())
overlayKey='currentPending12NormalSourceTestTrace20261108';assert overlayKey not in wb
O.mkdir()
for name,data in [('source-trace.json',rows),('proof-groups.json',groups),('test-trace.json',tests),('owner-corrections.json',ownerChanges)]:
 (O/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
refs={name:sha(O/name) for name in ('source-trace.json','proof-groups.json','test-trace.json','owner-corrections.json')}
overlay=dict(sourcePrograms=12,originalIndependentProofGroups=10,testSourceFiles=len(tests),previouslyExecutedCaseIds=96,newTests=0,newAcceptance=0,registeredComponentDelta=None,traceManifest=str((O/'manifest.json').relative_to(R)),sourceTrace=dict(path=str((O/'source-trace.json').relative_to(R)),sha256=refs['source-trace.json']),originalRunOrExecUnion=False,whole451Accepted=False,formalUpdated=False,canonicalOwnerFixes=3)
wb[overlayKey]=overlay
# Retain old inventory-count snapshot rather than silently changing its meaning.
wb[overlayKey]['legacyCountsNotReinterpreted']=True
wp.write_text(json.dumps(wb,ensure_ascii=False,indent=2)+'\n')
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),source=cfg['productionMain'],config=dict(path=str(C.relative_to(R)),sha256=sha(C)),supplement=dict(path=str(D.relative_to(R)),sha256=sha(D)),wbsBefore=cfg['wbsBefore'],wbsAfter=dict(path=str(wp.relative_to(R)),sha256=sha(wp)),overlayKey=overlayKey,sourcePrograms=12,proofGroups=10,testSourceFiles=len(tests),existingExecutedCaseIds=96,newTestExecutions=0,canonicalOwnerChanges=3,missingMainRowsAdded=1,sharedBootstrapOwnerCorrections=2,artifactRowsBefore=941,artifactRowsAfter=942,sourceMutation=False,productTestsExecuted=0,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,registeredComponentDelta=None,manualCoverageExclusions=[],oldExecCombined=False,files=refs,bugs=['BUG-2502'],ykts=['YKT-2240'],tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sources=12,proofs=10,testFiles=len(tests),existingCases=96,ownerCorrections=3,mainRowsAdded=1,manifestSha256=sha(O/'manifest.json'))))
