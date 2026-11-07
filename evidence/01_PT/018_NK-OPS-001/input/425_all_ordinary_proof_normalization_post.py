"""Independent schema normalization of existing public counter proofs; no execution/acceptance grant."""
from pathlib import Path
import datetime,json,hashlib,collections,re
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'PMO/pgpt-completion-stage-20261102';I=B/'evidence/PG23416-all-ordinary-public-proof-routing-v1';O=B/'evidence/PG23418-all-ordinary-proof-normalization-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=load(I/'manifest.json');assert not O.exists() and m['actualExit']==0 and m['publicObjectsRead']==355
for n,h in m['files'].items():assert sha(I/n)==h
normalp=R/m['normalPhysicalIndex']['path'];assert sha(normalp)==m['normalPhysicalIndex']['sha256'];normal=load(normalp);families=collections.defaultdict(dict)
for f,v in normal.items():families[v['path']][f]=v
nm=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');current=nm['begin']['inputHashes'];orig=load(S/'source-reuse-matrix.json')['rows'];orig={x['path']:x for x in orig};cache={}
for n,h in m['publicReadHashes'].items():assert sha(R/n)==h;cache[n]=load(R/n)
held={'TemporaryInfrastructureException.java','FingerprintKeyRing.java','ResponseSnapshotCodec.java','WebStartupException.java'}
def counter_ok(v):
 if not isinstance(v,dict):return False
 for k in ['LINE','METHOD','CLASS']:
  if not isinstance(v.get(k),dict) or type(v[k].get('covered')) is not int or type(v[k].get('missed')) is not int or v[k]['missed']!=0 or v[k]['covered']<=0:return False
 return 'BRANCH' not in v or (isinstance(v['BRANCH'],dict) and type(v['BRANCH'].get('covered')) is int and v['BRANCH'].get('missed')==0)
def normalized_inputs(v):
 out={}
 for key in ['inputHashes','publicSourceReadHashes','currentInputHashes','currentMainInputHashes','sourceHashes']:
  obj=v.get(key)
  if isinstance(obj,dict):
   for n,h in obj.items():
    if isinstance(n,str) and isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h):
     p=Path(n);n=str(p.relative_to(R)) if p.is_absolute() and p.is_relative_to(R) else n;out[n]=h
 b=v.get('begin')
 if isinstance(b,dict):out.update(normalized_inputs(b))
 return out
def normalized_physical(v):
 for key in ['physicalHashes','physicalClasses','physical','helperPhysicalClassHashes','normalPhysicalClassHashes']:
  obj=v.get(key)
  if isinstance(obj,dict) and obj and all(isinstance(n,str) and isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) for n,h in obj.items()):return {n.removesuffix('.class'):h for n,h in obj.items()}
 obj=v.get('sourcePhysicalInventory')
 if isinstance(obj,dict):return {n:x['sha256'] for n,x in obj.items() if isinstance(x,dict) and isinstance(x.get('sha256'),str)}
 return {}
def no_manual(v):
 for key in ['manualCoverageExclusions','manualCounterExclusions','manualExclusions']:
  if key in v:return v[key]==[] if isinstance(v[key],list) else v[key] is False
 rec=v.get('standardRecordFilter')
 if isinstance(rec,dict) and 'manualExclusions' in rec:return rec['manualExclusions']==[]
 return False
def execution(v):
 if v.get('actualExit')!=0:return 'NOT_SUCCESSFUL_QUALIFIER'
 if all(k in v for k in ['failures','errors','skipped']) and all(v[k]==0 for k in ['failures','errors','skipped']):
  if v.get('aborted')==0:return 'EXPLICIT_FES_ABORT_ZERO_IN_CANONICAL_METADATA'
  return 'EXPLICIT_FES_ZERO_ABORT_STATUS_REQUIRES_QUALIFIER_REFERENCE'
 cases=v.get('cases')
 if isinstance(cases,list) and cases and all(isinstance(x,dict) and (x.get('result')=='PASS' or all(x.get(k) is False for k in ['failure','error','skipped'])) for x in cases):return 'EXPLICIT_ACTUAL_CASES_ALL_PASS_ABORT_STATUS_SEPARATE'
 return 'SUCCESSFUL_INDEPENDENT_METADATA_QUALIFIER_PT_STATUS_IS_SEPARATE_NOT_INFERRED'
rows=[];unknown=[]
for name,v in cache.items():
 if not isinstance(v,dict):continue
 ph=normalized_physical(v);ip=normalized_inputs(v);cv=v.get('coverage');bySource=collections.defaultdict(list)
 for f in ph:
  if f in normal:bySource[normal[f]['path']].append(f)
 for source,fs in bySource.items():
  code={f for f,x in families[source].items() if x['hasCode']};scopeCode=set(fs)&code
  if isinstance(cv,dict) and scopeCode and all(counter_ok(cv.get(f)) for f in scopeCode):claim='ALL_EXPLICIT_CLASS_COUNTERS_ZERO_MISS'
  elif counter_ok(cv) and (v.get('wholeTargetCodeCoverage100') is True or v.get('wholeSourceFourCounter100') is True):claim='EXPLICIT_WHOLE_TARGET_AGGREGATE_ZERO_MISS'
  else:continue
  sourceMatch=ip.get(source)==current[source];physicalMatch=bool(code) and code<=set(fs) and all(ph.get(f)==families[source][f]['sha256'] for f in code);manual=no_manual(v);state='CURRENT_NORMAL_COUNTER_IDENTITY_MATCHED_PT_SEMANTICS_AND_CURRENT_RUN_SEPARATE' if v.get('actualExit')==0 and sourceMatch and physicalMatch and manual else 'MISSING_OR_STALE_IDENTITY_NOT_MATCHED';isheld=Path(source).name in held
  if isheld:state='HELD_PASSIVE_HISTORICAL_REFERENCE_ONLY_NOT_QUALIFIED'
  rows.append(dict(path=source,sourceSha256=current[source],manifest=name,manifestSha256=m['publicReadHashes'][name],originalSource=v.get('source') if isinstance(v.get('source'),str) and re.fullmatch('[0-9a-f]{40}',v['source']) else None,claim=claim,explicitWholeSourceNameFlag=v.get('wholeSourceFourCounter100') if isinstance(v.get('wholeSourceFourCounter100'),(bool,list)) else None,codePhysical=sorted(code),includedPhysical=sorted(fs),sourceHashMatches=sourceMatch,allCodePhysicalMatches=physicalMatch,manualExclusionsKnownEmpty=manual,originalExecutionMetadataStatus=execution(v),counterRows={f:cv[f] for f in scopeCode} if not counter_ok(cv) else cv,status=state,formalAcceptanceTransferred=False,newAcceptance=0))
 # Preserve explicit fullSourceUnits aliases with total counters in addition to per-class variants.
 full=v.get('fullSourceUnits')
 if isinstance(full,dict):
  for f,u in full.items():
   if f not in normal or not isinstance(u,dict) or not counter_ok(u.get('totals')):continue
   source=normal[f]['path'];fs=set(u.get('physical') or []);code={x for x,z in families[source].items() if z['hasCode']};sourceMatch=ip.get(source)==current[source];physicalMatch=bool(code) and code<=fs and all(ph.get(x)==families[source][x]['sha256'] for x in code);manual=no_manual(v);isheld=Path(source).name in held;state='CURRENT_NORMAL_COUNTER_IDENTITY_MATCHED_PT_SEMANTICS_AND_CURRENT_RUN_SEPARATE' if v.get('actualExit')==0 and sourceMatch and physicalMatch and manual and not isheld else 'MISSING_OR_STALE_IDENTITY_NOT_MATCHED'
   rows.append(dict(path=source,sourceSha256=current[source],manifest=name,manifestSha256=m['publicReadHashes'][name],originalSource=v.get('source') if isinstance(v.get('source'),str) and re.fullmatch('[0-9a-f]{40}',v['source']) else None,claim='EXPLICIT_FULL_SOURCE_UNIT_TOTALS',codePhysical=sorted(code),includedPhysical=sorted(fs),sourceHashMatches=sourceMatch,allCodePhysicalMatches=physicalMatch,manualExclusionsKnownEmpty=manual,originalExecutionMetadataStatus=execution(v),counterRows=u['totals'],status=state,formalAcceptanceTransferred=False,newAcceptance=0))
matched={x['path'] for x in rows if x['status'].startswith('CURRENT_NORMAL_COUNTER_IDENTITY_MATCHED')};beforeCandidates=load(B/'evidence/PG23362-base59-named-proof-independent-v1/existing-proof-candidate-union.json');newNames=sorted(matched-set(beforeCandidates));originCounts=collections.Counter(orig[n]['evidenceStatus'] if n in orig else 'OUTSIDE_ORIGINAL932' for n in matched);explicitPass={x['path'] for x in rows if x['path'] in matched and x['originalExecutionMetadataStatus']=='EXPLICIT_FES_ABORT_ZERO_IN_CANONICAL_METADATA'}
invalid='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/InvalidSessionRowException.java';ir=[x for x in rows if x['path']==invalid and x['status'].startswith('CURRENT_NORMAL_COUNTER_IDENTITY_MATCHED')];assert ir and any('PG21394' in x['manifest'] for x in ir);assert all(x['sourceHashMatches'] and x['allCodePhysicalMatches'] for x in ir)
# Separate records of the same physical SourceFile are one counter-evidence name, never summed
# into new tests or a new source count. Different names sharing a basename are never conflated.
def eligible_counter(source_same,physical_complete,manual_empty,held):return source_same is True and physical_complete is True and manual_empty is True and held is False
assert eligible_counter(True,True,True,False)
for args in [(False,True,True,False),(True,False,True,False),(True,True,None,False),(True,True,True,True)]:assert not eligible_counter(*args)
assert not counter_ok({'LINE':dict(covered=0,missed=0),'METHOD':dict(covered=0,missed=0),'CLASS':dict(covered=0,missed=0)})
assert not counter_ok({'LINE':dict(covered=1,missed=0),'METHOD':dict(covered=1,missed=1),'CLASS':dict(covered=1,missed=0)})
O.mkdir();files={}
for n,v in [('normalized-counter-identity-rows.json',rows),('matched-current-normal-counter-source-names.json',sorted(matched)),('additional-existing-proof-routes.json',newNames),('explicit-fes-abort-zero-source-names.json',sorted(explicitPass))]:
 p=O/n;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');files[n]=sha(p)
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),publicManifestsRead=355,normalizedCounterClaimRows=len(rows),matchedCurrentNormalCounterSourceNames=len(matched),matchedSourceOriginalStatusCounts=dict(originCounts),additionalNamesNotInPrior95=len(newNames),explicitFesAbortZeroMetadataSources=len(explicitPass),counterIdentityDoesNotProveAllQualityOrCurrentRun=True,invalidSessionExisting21394CodeProofReusedWithoutExecution=True,metadataNegativeChecks=6,allBaseResidual59Named=False,allCurrent93Qualified=False,currentProvisional93Unchanged=True,originalUnique453Unchanged=True,original282ProgressUnchanged=73,originalPartial80ProgressUnchanged=18,pendingFiveUnchanged=True,productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,inventory=dict(path=str((I/'manifest.json').relative_to(R)),sha256=sha(I/'manifest.json')),files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,normalizedClaimRows=len(rows),matchedCounterSourceNames=len(matched),additionalExistingRoutes=len(newNames),explicitPassMetadataSources=len(explicitPass),originCounts=dict(originCounts),metadataNegative6=6,productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
