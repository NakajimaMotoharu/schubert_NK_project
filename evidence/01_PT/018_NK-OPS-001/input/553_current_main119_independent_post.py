"""Independent exact inventory-delta/owner/physical metadata check, no Main execution."""
from pathlib import Path
from collections import Counter
import copy,datetime,hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG23850-current-main119-inventory-register-v1';O=B/'evidence/PG23852-current-main119-inventory-independent-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='194b0f0827c5a1bb8664e68dd2e59199b55cc7bdd1208bfe97c58b489390404d'
assert m['actualExit']==m['newAcceptance']==0 and m['wholeG13Accepted'] is False and m['whole451Accepted'] is False
for n,h in m['files'].items():assert sha(P/n)==h
cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256']
choices=load(R/m['decisions']['path']);assert sha(R/m['decisions']['path'])==m['decisions']['sha256']
normal=Path(cfg['normalManifest']['path']);assert sha(normal)==cfg['normalManifest']['sha256'];normal=load(normal)
wp=R/m['wbsAfter']['path'];assert sha(wp)==m['wbsAfter']['sha256'];current=load(wp)
raw=subprocess.check_output(['git','show',cfg['observerHead']+':'+cfg['wbsBefore']['path']],cwd=R);assert hashlib.sha256(raw).hexdigest()==cfg['wbsBefore']['sha256'];before=json.loads(raw)
assert before['artifacts']==current['artifacts'][:len(before['artifacts'])] and len(before['artifacts'])==942
assert {k:v for k,v in before.items() if k!='artifacts'}=={k:v for k,v in current.items() if k not in ('artifacts',m['overlayKey'])}
tracked=subprocess.check_output(['git','ls-files','--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).splitlines()
assert sorted(tracked)==cfg['productionMainPaths']==load(P/'current-main-paths.json') and len(tracked)==967
assert subprocess.run(['git','diff','--quiet',cfg['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R).returncode==0
indexp=B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexp)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(indexp)
tasks={v['id']:v for v in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks']}
decisions={v['path']:v for v in choices['decisions']};added=load(P/'added-artifacts.json');evidence=load(P/'source-owner-proof.json')
assert added==current['artifacts'][942:]
oldPaths={v['path'] for v in before['artifacts']};assert set(tracked)-oldPaths==set(cfg['missingSourcePins'])
explicit={'ApiStopBudget.java':'WBS-P018-05','InboundConsumerGroup.java':'WBS-P005-03','LinuxSystemdSession.java':'WBS-P018-03','SystemManagerObservation.java':'WBS-P018-03','FailedJmsIsolationException.java':'WBS-P005-03','UnconfirmedJmsRollbackException.java':'WBS-P005-03','WebHttpLogKind.java':'WBS-P006-03'}
expectedOwners={n:explicit.get(Path(n).name,'WBS-P018-09') for n in cfg['missingSourcePins']}
assert Counter(expectedOwners.values())=={'WBS-P018-09':112,'WBS-P018-05':1,'WBS-P005-03':3,'WBS-P018-03':2,'WBS-P006-03':1}
for n,h in cfg['missingSourcePins'].items():
 assert not any(t in n for t in cfg['protectedNameTokens']);assert sha(R/n)==h==normal['begin']['inputHashes'][n]
 actual=(R/n).read_text();comment=re.search(r'/\*\*(.*?)\*/',actual,re.S)
 comment=' '.join(re.sub(r'^\s*\* ?', '',comment[1],flags=re.M).split()) if comment else None
 assert comment==decisions[n]['reviewedDeclaredResponsibility']
 assert expectedOwners[n]==decisions[n]['owner']==decisions[n]['costOwner']
 if Path(n).name not in explicit:
  assert '/monitoring/' in n and re.search('(?i)metric|monitor|observ|health|duration|export|registry|collector|record|count|label|usage',str(comment)+Path(n).name)
def valid(rows,proofs):
 try:
  assert len(rows)==119 and len(proofs)==119 and len({v['path'] for v in rows})==119
  assert {v['path'] for v in rows}=={v['path'] for v in proofs}==set(cfg['missingSourcePins'])
  byPath={v['path']:v for v in proofs}
  for v in rows:
   n=v['path'];e=byPath[n];d=decisions[n]
   assert n not in oldPaths and v['owner']==v['costOwner']==expectedOwners[n] and v['sha256']==cfg['missingSourcePins'][n]
   assert v['module']==n.split('/')[1].removeprefix('schubert-nk-')
   physical={k:x for k,x in index.items() if x['path']==n};assert physical and v['class'] in physical
   assert e['canonicalOwner']==e['canonicalCostOwner']==expectedOwners[n] and e['program']==tasks[expectedOwners[n]]['program']
   assert e['sourceSha256']==v['sha256'] and e['reason']==d['reason'] and e['reviewedDeclaredResponsibility']==d['reviewedDeclaredResponsibility']
   assert e['wholeSourcePhysicalClasses']==sorted(physical) and e['physicalClassHashes']=={k:x['sha256'] for k,x in physical.items()} and e['physicalClassHasCode']=={k:x['hasCode'] for k,x in physical.items()}
   code=any(x['hasCode'] for x in physical.values());assert e['noExecutableCodeInSource'] is (not code) and e['noCodeCounterRatio'] is None
   assert v['counterApplicability']==('EXECUTABLE_OR_MEASUREMENT_REQUIRED' if code else 'NO_EXECUTABLE_CODE_METADATA_PHYSICAL_RETAINED')
   assert e['coverageQualified'] is False and e['wholeRequirementTraceAccepted'] is False and e['wholeG13Accepted'] is False and v['acceptance']=='UNASSESSED'
  return True
 except (AssertionError,KeyError,TypeError):return False
assert valid(added,evidence)
assert len(current['artifacts'])==1061 and len({v['path'] for v in current['artifacts']})==1061
assert set(tracked)<={v['path'] for v in current['artifacts']}
assert sum(v['noExecutableCodeInSource'] for v in evidence)==6 and sum(v['isPackageAnnotationMetadata'] for v in evidence)==3
negatives=[]
for label,change in [('missing-path',lambda v:v.pop()),('duplicate-path',lambda v:v.append(copy.deepcopy(v[0]))),('wrong-owner',lambda v:v[0].update(owner='WBS-P019-01')),('wrong-cost-owner',lambda v:v[0].update(costOwner='WBS-P019-01')),('wrong-source-hash',lambda v:v[0].update(sha256='0'*64)),('wrong-physical-module',lambda v:v[0].update(module='web')),('fake-acceptance',lambda v:v[0].update(acceptance='ACCEPTED'))]:
 altered=copy.deepcopy(added);change(altered);assert not valid(altered,evidence);negatives.append(label)
altered=copy.deepcopy(evidence);nocode=next(v for v in altered if v['noExecutableCodeInSource']);nocode['noExecutableCodeInSource']=False;assert not valid(added,altered);negatives.append('NoCode-to-Code')
altered=copy.deepcopy(evidence);altered[0]['coverageQualified']=True;assert not valid(added,altered);negatives.append('inventory-to-coverage-pass')
altered=copy.deepcopy(evidence);altered[0]['wholeSourcePhysicalClasses'].pop();assert not valid(added,altered);negatives.append('missing-physical')
overlay=current[m['overlayKey']];assert overlay['mainPathCount']==overlay['registeredAfter']==967 and overlay['registeredBefore']==848 and overlay['missingAfter']==overlay['duplicateCurrentPaths']==0
assert overlay['newProductTests']==overlay['newAcceptance']==0 and overlay['wholeG13Accepted'] is False and overlay['whole451Accepted'] is False and overlay['effortRate'] is None
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],producer=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),wbsAfter=m['wbsAfter'],mainPaths=967,registeredBefore=848,registeredAfter=967,missingAfter=0,addedRows=119,ownerCounts=dict(Counter(expectedOwners.values())),noExecutableCodeSources=6,packageAnnotationMetadataSources=3,allOld942RowsAndUnrelatedValuesPreserved=True,independentMetadataNegativeChecks=len(negatives),negativeLabels=negatives,sourceMutation=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,bugs=['BUG-2504'],ykts=['YKT-2242'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,main=967,registered=967,added=119,missing=0,negativeChecks=len(negatives),manifestSha256=sha(O/'manifest.json'))))
