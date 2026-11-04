import json,hashlib,collections,os,datetime
from pathlib import Path
from g07_host_class_provenance_inputs import write
root=Path.cwd();base=root/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
source=json.loads((base/'504_通常PT参照判定.json').read_bytes())
review=json.loads((base/'539_意味レビュー二十四件の原通常PT宣言exact対応.json').read_bytes())
packages=json.loads((base/'502_残作業leaf・終了条件.json').read_bytes())['packages']
reviewed={r['id'] for r in review['rows']}
held={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'}
references=collections.defaultdict(list)
for p in packages:
 for path in p['definitionOfDone'][0]['input']['candidateTestFiles']:
  references[path].append(dict(wbs=p['packageId'],requirements=p['requirements'],ss=p['ss'],costOwner=p['costOwner'],specDirectory=p['definitionOfDone'][0]['input']['specDirectory']))
byFile=collections.defaultdict(list)
for r in source['rows']:
 if r['decision']=='CURRENT_EXECUTION_REFERENCE_MISSING_RECONCILIATION_REQUIRED':byFile[r['path']].append(r)
packets=[]
for i,(path,rows) in enumerate(sorted(byFile.items()),1):
 hashes={r['sha256'] for r in rows};assert len(hashes)==1
 done=[r for r in rows if r['id'] in reviewed];blocked=path.rsplit('/',1)[-1] in held
 owners=sorted({x['costOwner'] for x in references[path] if x['costOwner']})
 packets.append(dict(packetId='S-ORACLE-'+str(i).zfill(3),path=path,inputSha256=next(iter(hashes)),caseRows=[dict(id=r['id'],span=r['span'],staticSemanticReviewPerformed=r['id'] in reviewed) for r in rows],missingCurrentReferences=len(rows),staticallyReviewedMethods=len(done),remainingMethodReview=len(rows)-len(done),heldSourceRead=blocked,sourceFilesReadByThisProducer=False,explicitWbsReferences=references[path],costOwner=owners[0] if len(owners)==1 else None,costOwnerStatus='EXPLICIT_SINGLE_REFERENCE_NOT_NEW_ALLOCATION' if len(owners)==1 else 'CANONICAL_PRIMARY_NOT_RESOLVED_DO_NOT_SPLIT_OR_DOUBLE_CHARGE',planStatus='SOURCE_READ_HELD_PUBLIC_ORACLE_WORK_ONLY' if blocked else 'STATIC_METHOD_REVIEW_COMPLETE_DYNAMIC_OR_REUSE_DECISION_OPEN' if len(done)==len(rows) else 'ADDITIONAL_SEMANTIC_QUALIFICATION_WORK_REQUIRED',requiredSteps=['Independent SS/UI expected values per named method, fixture, null/error/boundary/postconditions','Whole-class initializer/helper/side-effect and exact class HOLD intersection review; no operation probing','Source/byte/runtime references checked before reuse; otherwise define the truly missing qualification','Explicit criteria/parent exits and canonical primary cost owner; no budget by declaration count'],proposedRuntimeCommand=None,necessaryNewProductRuns=None,newPtPasses=0,newAcceptance=False,coverageAdded=0,estimatedPp=dict(low=None,base=None,high=None),costCountingRole='PLANNING_BREAKDOWN_REFERENCES_EXISTING_WBS_NO_NEW_BUDGET'))
assert sum(p['missingCurrentReferences'] for p in packets)==2980 and sum(p['staticallyReviewedMethods'] for p in packets)==24
out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18522-ordinary-missing-class-packets-v1';assert not out.exists();out.mkdir()
value=dict(actualExit=0,source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',scope='ALL2980_MISSING_ORDINARY_REFERENCES_GROUPED_FOR_SEMANTIC_REVIEW_NOT_NEW_EXECUTION_UNITS',packets=packets,totalMissing=2980,reviewedMethods=24,remainingReviewMethods=2956,classFilePackets=len(packets),wholeClassReviewsDone=sum(p['remainingMethodReview']==0 for p in packets),heldSourcePackets=sum(p['heldSourceRead'] for p in packets),wholeMeaningClassificationAccepted=False,productTests=0,newAcceptedCriteria=0,allUnreferencedAssumedUnexecuted=False,noSameNameCaseAliasing=True,wholeClassNotDynamicallySplitToAvoidHolds=True)
value['atJST']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
value['wholeClassReviewsDoneMeaning']='All missing methods in the file reviewed; not a Product acceptance or implicit qualification of other methods/hooks.'
write(out/'manifest.json',value)
with (out/'manifest.json').open('rb') as handle:os.fsync(handle.fileno())
summary=dict(actualExit=0,packets=len(packets),missing=2980,reviewed=24,remainingReview=2956,fullyReviewedFiles=value['wholeClassReviewsDone'],heldFiles=value['heldSourcePackets'],counts=dict(collections.Counter(p['planStatus'] for p in packets)),manifestSha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),manifestBytes=(out/'manifest.json').stat().st_size,productTests=0)
payload=json.dumps(summary);assert len(payload.encode())<=4096;print(payload)
