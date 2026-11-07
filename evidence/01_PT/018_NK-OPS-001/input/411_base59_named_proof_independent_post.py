"""Independently separate passive references from proof candidates and bind prior pure five PT."""
from pathlib import Path
import datetime,hashlib,json,collections,copy,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'evidence/PG23360-base59-named-proof-supplement-v1';O=B/'evidence/PG23362-base59-named-proof-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=load(I/'manifest.json');assert not O.exists() and m['actualExit']==0 and m['qualificationFields']==19 and m['productTestsExecuted']==0
for n,h in m['files'].items():assert sha(I/n)==h
for n,h in m['publicManifestReads'].items():assert sha(R/n)==h
rows=load(I/'supplemental-source-candidates.json');assert len(rows)==27;physical=load(I/'current-normal-physical-index.json');assert len(physical)==m['normalClassFiles'];normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==m['normalManifestSha256'];nm=load(normal)
held={'TemporaryInfrastructureException.java','FingerprintKeyRing.java','ResponseSnapshotCodec.java','WebStartupException.java'};metadataOnly=[];candidates=[]
for row in rows:
 assert row['wholeQualificationTransferred'] is False and row['currentSourceSha256']==nm['begin']['inputHashes'][row['path']];assert all(physical[n]==v for n,v in row['normalPhysical'].items());assert {n for n,v in physical.items() if v['path']==row['path']}==set(row['normalPhysical'])
 v=copy.deepcopy(row)
 if Path(row['path']).name in held:v.update(selectionState='ZERO_HIT_OR_PASSIVE_REFERENCE_ONLY_HELD_NOT_QUALIFICATION_CANDIDATE',automaticUnitAllowed=False);metadataOnly.append(v)
 else:v.update(selectionState='EXISTING_PUBLIC_QUALIFICATION_REFERENCE_REQUIRES_INDIVIDUAL_PROOF_REVIEW',automaticUnitAllowed=False);candidates.append(v)
assert len(metadataOnly)==4 and len(candidates)==23
prior=load(B/'evidence/PG23274-named-roster-duplicate-post-v1/candidate-source-rows.json');oldNames={v['path'] for v in prior};names=sorted(oldNames|{v['path'] for v in candidates});assert len(oldNames)==87 and len(names)==95
q=load(I/'existing-question-five-proof.json');qp=R/q['proof']['path'];assert sha(qp)==q['proof']['sha256'];qm=load(qp);assert qm['actualExit']==0 and qm['tests']==5 and qm['wholeSourceFourCounter100'] and qm['oldExecUnion'] is False;assert qm['failures']==qm['errors']==qm['skipped']==qm['aborted']==0 and all(v==0 for v in qm['heldFourProbeHits'].values());source=q['path'];assert sha(R/source)==q['sourceSha256']==qm['inputHashes'][source];n='dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata';assert q['physical'][n]==physical[n] and qm['physicalHashes'][n]==physical[n]['sha256'] and qm['physicalClassIds'][n]==physical[n]['crc64'];assert {k:qm['coverage'][n][k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=9,METHOD=2,CLASS=1,BRANCH=4);assert all(v['missed']==0 for v in qm['coverage'][n].values());assert len([v for v in physical.values() if v['path']==source])==1
# Both existing Test files still match the old successful five's input pins. No Test is executed.
tests=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/'+v+'.java' for v in ['QuestionCommandTimeBoundaryTest','QuestionCommandMetadataContractTest']];testPins={p:sha(R/p) for p in tests};assert all(qm['inputHashes'][p]==h for p,h in testPins.items())
assert not subprocess.check_output(['git','diff','--name-only',nm['source'],'HEAD','--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()
# Independent metadata negatives: candidate status does not prove whole coverage, zero-hit held
# references never permit Unit, and an old same-source proof requires identical physical bytes.
def admissible(v):return v.get('actualExit')==0 and v.get('sourceEqual') is True and v.get('physicalEqual') is True and v.get('allApplicableCovered') is True and v.get('scope')=='COUNTER_SUBPROOF_ONLY'
base=dict(actualExit=0,sourceEqual=True,physicalEqual=True,allApplicableCovered=True,scope='COUNTER_SUBPROOF_ONLY');assert admissible(base)
neg=0
for k,v in [('sourceEqual',False),('physicalEqual',False),('allApplicableCovered',None),('scope','WHOLE451_OR_NEW_ACCEPTANCE')]:
 x=dict(base);x[k]=v;assert not admissible(x);neg+=1
assert all(not v['automaticUnitAllowed'] for v in candidates+metadataOnly);neg+=1
oldgate=load(B/'evidence/PG23350-existing-proof-selection-gate-v1/selection-rows.json');gate=[]
for v in oldgate:
 x=copy.deepcopy(v)
 if x['path'] in names and x['decision'].startswith(('PARTIAL_','UNBOUND_')):x.update(decision='EXISTING_NAMED_OR_PENDING_PROOF_REVIEW_FIRST_NO_AUTOMATIC_UNIT',supplementalProofRoute=str((O/'manifest.json').relative_to(R)))
 gate.append(x)
O.mkdir();files={}
for name,value in [('existing-proof-candidate-union.json',names),('held-passive-references-not-candidates.json',metadataOnly),('supplemental-proof-candidates.json',candidates),('updated-selection-rows.json',gate),('question-existing-five-counter-subproof.json',dict(q,currentTestInputHashes=testPins,originalTestRerun=0,actualNewPtCount=0,wholeWbsAccepted=False,allSourceRunAccepted=False))]:
 p=O/name;p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');files[name]=sha(p)
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalManifest=dict(path=str((I/'manifest.json').relative_to(R)),sha256=sha(I/'manifest.json')),finiteOldQualificationFields=19,publicManifestReads=22,referenceNamesBeforeClassification=99,heldPassiveReferenceNames=4,eligibleExistingProofCandidateNames=95,previousCandidateNames=87,additionalNonHeldCandidates=8,metadataNegativeChecks=neg,questionFiveExistingWholeCounterSubproofBound=True,questionOriginalSource=q['oldSource'],questionCurrentNormalSource=nm['source'],questionTestSourceHashes=testPins,questionRegisteredComponentDelta=0,originalPartial80ProgressUnchanged=18,allBase59Qualified=False,allCurrent93Qualified=False,productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingProofCandidateNames=95,heldReferences=4,metadataNegatives=neg,questionFiveReplayed=0,newAcceptance=0,manifestSha256=sha(O/'manifest.json'))))
