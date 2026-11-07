"""Finite public ended-group/ledger reference routing; no Product, private raw or test replay."""
from pathlib import Path
import datetime,json,hashlib,re,collections
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'PMO/pgpt-completion-stage-20261102';O=B/'evidence/PG23416-all-ordinary-public-proof-routing-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());assert not O.exists();ep=R.parent/'PMO/pgpt-execution-metrics/events.jsonl';raw=ep.read_bytes();events=[json.loads(x) for x in raw.splitlines()];ends=[e for e in events if (e.get('eventType')=='GROUP_END' or e.get('groupBoundary')=='END') and e.get('timeJST','')>='2026-11-04'];cost=load(S/'cost-ledger.json');normalp=B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';normal=load(normalp);sourcePhysical=collections.defaultdict(dict)
for n,v in normal.items():sourcePhysical[v['path']][n]=v
matrixp=S/'source-reuse-matrix.json';matrix=load(matrixp);original={v['path']:v for v in matrix['rows']};normalManifest=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');currentHashes=normalManifest['begin']['inputHashes'];forbidden=('RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness');held={'TemporaryInfrastructureException.java','FingerprintKeyRing.java','ResponseSnapshotCodec.java','WebStartupException.java'}
refs={};declines=[];eventRows=[]
def canonical(n):
 if not isinstance(n,str) or not n.endswith('.json'):return None
 p=Path(n)
 if '..' in p.parts or any(x in n for x in forbidden):return None
 p=R/p if not p.is_absolute() else p
 if not p.is_relative_to(R) or not str(p.relative_to(R)).startswith('evidence/01_PT/'):return None
 return str(p.relative_to(R))
def add(n,h,origin):
 n=canonical(n)
 if not n:return
 v=refs.setdefault(n,dict(path=n,expectedHashes=[],origins=[]))
 if isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) and h not in v['expectedHashes']:v['expectedHashes'].append(h)
 if origin not in v['origins']:v['origins'].append(origin)
def walk(x,origin,depth=0):
 if depth>12:return
 if isinstance(x,dict):
  if isinstance(x.get('path'),str):add(x['path'],x.get('sha256'),origin)
  for k,v in x.items():
   if isinstance(v,str) and v.endswith('.json'):add(v,x.get(k+'Sha256'),dict(origin,field=k))
   elif isinstance(v,(dict,list)):walk(v,dict(origin,field=k),depth+1)
 elif isinstance(x,list):
  for v in x:walk(v,origin,depth+1)
for e in ends:
 t=e.get('technicalMeasurementDelta') or {};claims={k:v for k,v in t.items() if k in ['wholeJavaSourceProofs','newWholeSourceProofs','newSourceQualifications','newDirectWholeSourceProof','currentDirectWholeSourceProof','newSourceProofs','reusedWholeSourceSubproofs']};hint=[v['path'] for v in t.get('coverageBySource',[]) if isinstance(v,dict) and isinstance(v.get('path'),str) and v['path'].endswith('.java')];eventRows.append(dict(eventId=e['eventId'],groupId=e['groupId'],workCategory=e.get('workCategory'),timeJST=e['timeJST'],claimFields=claims,explicitSourceNames=hint,sourceEvidenceRefs=e.get('sourceEvidenceRefs') or [],rawWholeSourcesFieldPresent='wholeSources' in t));walk(e,dict(kind='PUBLIC_GROUP_END',eventId=e['eventId'],groupId=e['groupId']))
walk(cost['ordinaryGroups'],dict(kind='LEGACY_OR_CURRENT_ORDINARY_GROUP_LEDGER'));walk(cost['componentActivities'],dict(kind='COMPONENT_ACTIVITY_LEDGER'))
for k,v in cost.items():
 if isinstance(v,dict) and ('qualification' in k.lower() or k in ['resolvedNamedWholeSourceProofs','pendingNamedWholeSourceProofs']):walk(v,dict(kind='QUALIFICATION_LEDGER',field=k))
# Explicitly discovered existing two-test reference; no source/test/runtime is replayed.
for n,h in [('evidence/01_PT/015_NK-WEB-001/evidence/PG21394-invalid-row-two-v1/manifest.json','f89ac2f2e56cd515617e744a6734fcde167e0cecac1eb3e99909fad1eb8a443d'),('evidence/01_PT/015_NK-WEB-001/evidence/PG21402-invalid-row-independent-post-v1/manifest.json','672fd714ba23cb40af051b5406c034f096ef5a80577ea89962afcc83b376495a')]:add(n,h,dict(kind='EXISTING_PROGRAM_RESULT_015077'))
cache={};queue=list(refs);schemas=collections.Counter();shapes=[]
for n in queue:
 p=R/n
 if any(x.is_symlink() for x in [p,*list(p.parents)[:len(p.relative_to(R).parts)-1]]):declines.append(dict(path=n,reason='SYMLINK_BEFORE_CONTENT_READ'));continue
 if not p.is_file():declines.append(dict(path=n,reason='REFERENCED_PUBLIC_JSON_MISSING'));continue
 if p.stat().st_size>2*1024*1024:declines.append(dict(path=n,reason='ABOVE_DECLARED_2M_PUBLIC_METADATA_BOUND'));continue
 actual=sha(p);expected=refs[n]['expectedHashes']
 if expected and actual not in expected:declines.append(dict(path=n,reason='EXPECTED_HASH_MISMATCH_UNTRUSTED_NOT_REUSED',actualSha256=actual,expectedHashes=expected));continue
 try:v=load(p)
 except (ValueError,UnicodeError):declines.append(dict(path=n,reason='REFERENCED_JSON_UNREADABLE_NOT_REUSED'));continue
 if not isinstance(v,dict):declines.append(dict(path=n,reason='NON_OBJECT_PUBLIC_JSON_REFERENCE_NOT_MANIFEST'));continue
 cache[n]=v;schema=tuple(k for k in ['fullSourceUnits','sourceFilePhysicalClosure','wholeSourceFourCounter100','wholeTargetCodeCoverage100','completeSourceCoverageMeasured','coverage','physical','physicalHashes','physicalClasses','sourcePhysicalInventory','inputHashes','publicSourceReadHashes','actualExit','tests','cases'] if k in v);schemas[str(schema)]+=1;shapes.append(dict(path=n,sha256=actual,schema=list(schema),actualExit=v.get('actualExit'),tests=v.get('tests'),qualification=v.get('qualification') if isinstance(v.get('qualification'),str) else None,originalRefs=refs[n]))
 # At most one manifest-internal hop for public raw result JSON or explicit independent proof.
 # No private run manifest, logs, exec, XML, archive or test/source file content is accessed.
 if len(queue)<800:
  before=set(refs);walk({k:x for k,x in v.items() if k in ['originalManifest','independentPost','post','staticPreflight','upstream','fullSourceProofs','counterSubproofRefs']},dict(kind='ONE_HOP_PUBLIC_MANIFEST',parent=n))
  for child in sorted(set(refs)-before):
   if child not in queue:queue.append(child)
  for f,h in (v.get('files') or {}).items() if isinstance(v.get('files'),dict) else []:
   if f in ['original-manifest.json','original-manifest.safe.json','original-begin.json']:
    child=str((Path(n).parent/f));add(child,h,dict(kind='HASHED_COPIED_RESULT_METADATA',parent=n))
    if child not in queue:queue.append(child)
assert len(queue)<800
# Route only explicit full-SourceFile/class targets. Universal inputHashes are source identity,
# never an execution target set. Full qualification requires all Code/current physical and source.
proofRows=[]
def counters(x):return isinstance(x,dict) and all(k in x and isinstance(x[k],dict) and isinstance(x[k].get('covered'),int) and isinstance(x[k].get('missed'),int) for k in ['LINE','METHOD','CLASS']) and all(x[k]['missed']==0 for k in ['LINE','METHOD','CLASS']) and (not x.get('BRANCH') or x['BRANCH'].get('missed')==0)
def pins(v):
 for key in ['physicalHashes','physicalClasses','physical']:
  x=v.get(key)
  if isinstance(x,dict) and x and all(isinstance(k,str) and isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) for k,h in x.items()):return {k.removesuffix('.class'):h for k,h in x.items()}
 inv=v.get('sourcePhysicalInventory')
 if isinstance(inv,dict):return {k:z['sha256'] for k,z in inv.items() if isinstance(z,dict) and isinstance(z.get('sha256'),str)}
 return {}
def inputpins(v):
 result={}
 for x in [v.get('inputHashes'),v.get('publicSourceReadHashes'),(v.get('begin') or {}).get('inputHashes') if isinstance(v.get('begin'),dict) else None]:
  if isinstance(x,dict):
   for k,h in x.items():
    if isinstance(k,str) and isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h):
     p=Path(k);k=str(p.relative_to(R)) if p.is_absolute() and p.is_relative_to(R) else k;result[k]=h
 return result
for n,v in cache.items():
 ph=pins(v);ip=inputpins(v);unitCandidates=[];full=v.get('fullSourceUnits')
 if isinstance(full,dict):
  for f,u in full.items():
   if isinstance(u,dict) and counters(u.get('totals')) and u.get('metadataOnly') is False and (u.get('threeCounter100') is True or u.get('four100') is True):unitCandidates.append((f,list(u.get('physical') or [f]),u['totals'],'EXPLICIT_FULL_SOURCE_UNIT'))
 elif v.get('wholeSourceFourCounter100') is True or v.get('wholeTargetCodeCoverage100') is True:
  cv=v.get('coverage');bySource=collections.defaultdict(list)
  for f in ph:
   if f in normal:bySource[normal[f]['path']].append(f)
  for source,fs in bySource.items():
   if counters(cv):unitCandidates.append((fs[0],fs,cv,'WHOLE_TARGET_AGGREGATE_ZERO_MISS_WITH_EXPLICIT_PHYSICAL'))
   elif isinstance(cv,dict) and all(counters(cv.get(f)) for f in fs):unitCandidates.append((fs[0],fs,{f:cv[f] for f in fs},'WHOLE_SOURCE_FLAG_WITH_CLASS_COUNTERS'))
 for f,fs,cv,schema in unitCandidates:
  if f not in normal:proofRows.append(dict(path=None,manifest=n,manifestSha256=sha(R/n),className=f,status='OUTSIDE_CURRENT_SIX_MAIN_PHYSICAL_INDEX_NOT_QUALIFIED',schema=schema));continue
  source=normal[f]['path'];family=sourcePhysical[source];code={k for k,x in family.items() if x['hasCode']};included=set(fs);sourceMatch=ip.get(source)==currentHashes[source];physicalMatch=bool(code) and code<=included and all(ph.get(k)==family[k]['sha256'] for k in code);manual=v.get('manualCoverageExclusions',v.get('manualCounterExclusions'));manualKnownEmpty=manual==[];heldOnly=Path(source).name in held
  state='CURRENT_SOURCE_AND_ALL_NORMAL_CODE_MATCH_COUNTER_SUBPROOF_ONLY' if v.get('actualExit')==0 and sourceMatch and physicalMatch and manualKnownEmpty and not heldOnly else 'NOT_CURRENT_QUALIFIED_REQUIRES_MISSING_IDENTITY_OR_SCHEMA_REVIEW'
  if heldOnly:state='HELD_PASSIVE_HISTORICAL_REFERENCE_NOT_CURRENT_QUALIFICATION'
  proofRows.append(dict(path=source,sourceSha256=currentHashes[source],manifest=n,manifestSha256=sha(R/n),originalSource=v.get('source') if isinstance(v.get('source'),str) and re.fullmatch('[0-9a-f]{40}',v['source']) else None,schema=schema,normalCodePhysical=sorted(code),includedPhysical=sorted(included),sourceHashMatches=sourceMatch,allNormalCodePhysicalHashesMatch=physicalMatch,manualExclusionsKnownEmpty=manualKnownEmpty,counters=cv,status=state,formalAccepted=False,newAcceptance=0))
qualified={x['path'] for x in proofRows if x['status']=='CURRENT_SOURCE_AND_ALL_NORMAL_CODE_MATCH_COUNTER_SUBPROOF_ONLY'};originCounts=collections.Counter(original[n]['evidenceStatus'] if n in original else 'OUTSIDE_ORIGINAL932' for n in qualified);O.mkdir();files={}
for name,value in [('ended-group-claim-routing.json',eventRows),('public-manifest-shapes.json',shapes),('declined-public-references.json',declines),('source-counter-proof-routing.json',proofRows),('qualified-counter-subproof-source-names.json',sorted(qualified))]:
 p=O/name;p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');files[name]=sha(p)
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),endedGroups=len(ends),explicitPublicReferences=len(refs),publicObjectsRead=len(cache),declines=len(declines),sourceCounterClaimRows=len(proofRows),currentSourceCounterSubproofNames=len(qualified),currentSourceCounterSubproofOriginCounts=dict(originCounts),schemaCounts=dict(schemas),allBaseResidual59Named=False,allCurrent93Qualified=False,currentProvisional93Unchanged=True,originalUnique453Unchanged=True,original282ProgressUnchanged=73,originalPartial80ProgressUnchanged=18,pendingFiveUnchanged=True,productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,eventsObservedSha256=hashlib.sha256(raw).hexdigest(),lastEventAtSnapshot=events[-1]['eventId'],matrixSha256=sha(matrixp),normalPhysicalIndex=dict(path=str(normalp.relative_to(R)),sha256=sha(normalp)),publicReadHashes={n:sha(R/n) for n in cache},files=files,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,endedGroups=len(ends),publicObjectsRead=len(cache),declines=len(declines),counterClaimRows=len(proofRows),currentSourceCounterSubproofNames=len(qualified),origins=dict(originCounts),productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
