"""Independently verify metadata graph fixed point and finite cross-module/source closure guards."""
from pathlib import Path
import datetime,hashlib,json,collections,copy
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'evidence/PG23748-ordinary-reference-candidates-v1';O=B/'evidence/PG23756-ordinary-reference-candidates-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert not O.exists();m=load(I/'manifest.json');assert sha(I/'manifest.json')=='9396477029b96edfe5bc79ed644f57d996fa69e4c203a29e71ff6514bde8d169';cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256'];idx=load(B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json')
for n,pin in m['artifacts'].items():assert sha(I/n)==pin
for n,pin in cfg['publicInputs'].items():assert sha(R/n)==pin
rows=load(I/'source-candidates.json');parsed=load(I/'physical-symbols.json');byPath={x['mainPath']:x for x in rows};selected=set(cfg['selectedPhysicalNames'])
def scope_valid(names):
 assert names and len(names)==len(set(names))
 names=set(names)
 for n in names:
  v=idx[n];assert n not in cfg['excludedHeldFamilies'] and v['path'] not in cfg['excludedHeldSources'];assert v['path'].startswith(('src/schubert-nk-protocol/','src/schubert-nk-api/','src/schubert-nk-web/')) or v['path']=='src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java';assert {k for k,x in idx.items() if x['path']==v['path']}<=names
scope_valid(cfg['selectedPhysicalNames']);assert set(parsed)==selected and len(parsed)==946 and len(byPath)==len(rows)==676
for row in rows:
 n=row['mainPath'];assert set(row['physical'])=={k for k,x in idx.items() if x['path']==n};assert row['executionAuthorized'] is False and row['alreadyNamed']==(n in cfg['alreadyNamedCandidatePaths']);seen=set();queue=[n];labels=set();unknown=set()
 while queue:
  s=queue.pop()
  if s in seen:continue
  seen.add(s);v=byPath[s];labels.update(v['directReviewMarkers']);queue.extend(v['sourceEdges'])
  for physical in v['physical']:
   assert parsed[physical]['className']==physical and parsed[physical]['sourceFile']==Path(s).name
   for ref in parsed[physical]['references']:
    if ref.startswith('dev/codex/schubert/') and ref not in selected:unknown.add(ref)
 assert labels==set(row['transitiveReviewMarkers']) and unknown==set(row['unresolvedProductReferences'])
 assert row['hasCode']==any(idx[k]['hasCode'] for k in row['physical'])
 expected='REVIEW_REQUIRED_TRANSITIVE_MARKERS' if labels else 'ALREADY_NAMED_CODE_CANDIDATE_NOT_REQUALIFIED' if row['alreadyNamed'] else 'NATURAL_NO_CODE_NO_EXECUTION_REQUIRED' if not row['hasCode'] else 'NO_MARKED_REFERENCE_NEW_REVIEW_CANDIDATE_NOT_EXECUTION_AUTHORITY';assert expected==row['status']
assert dict(collections.Counter(x['status'] for x in rows))==m['sourceStatusCounts'];assert m['actualExit']==m['productTestsExecuted']==m['productClassesInitialized']==m['actualBackendActions']==m['newAcceptance']==0 and m['heldMemberBytesRead'] is m['protectedPathsRead'] is m['compilerOrJvmExecuted'] is m['coverageMeasured'] is m['formalUpdated'] is m['whole451Accepted'] is False and m['effortRate'] is None
before=B/'evidence/PG23752-ordinary-reference-scope-before-v1';beforeManifest=load(before/'manifest.json');assert sha(before/'manifest.json')=='6e7a348540fd9584ce7d5e70c97351dd7d6e8c6bd1a64de09102645344abf1b3'
for n,pin in beforeManifest['beforeFiles'].items():assert sha(before/n)==pin
old=load(before/'521_ordinary_reference_candidate_scope.json');negative=0
# Original invalid scope is rejected; fixing only module still rejects incomplete SourceFile.
variants=[old['selectedPhysicalNames'],[n for n in old['selectedPhysicalNames'] if idx[n]['path'].startswith(('src/schubert-nk-api/','src/schubert-nk-web/','src/schubert-nk-protocol/','src/schubert-nk-storage/'))],cfg['selectedPhysicalNames'][:-1],cfg['selectedPhysicalNames']+[cfg['selectedPhysicalNames'][0]],cfg['selectedPhysicalNames']+[cfg['excludedHeldFamilies'][0]]]
for names in variants:
 try:scope_valid(names)
 except AssertionError:negative+=1
 else:raise AssertionError('invalid namespace or partial source domain accepted')
assert negative==5
cross=[]
for n,module in [('500_service_db_admission_scope.json','bootstrap'),('506_service_database_source_scope.json','bootstrap')]:
 p=B/'input'/n;v=load(p);assert module in v['modules'] and 'storage' in v['modules'];targets=set(v['targetPhysical']);paths={idx[k]['path'] for k in targets};assert all(x.startswith('src/schubert-nk-bootstrap/') for x in paths) and {k for k,x in idx.items() if x['path'] in paths}==targets;cross.append(dict(scope=str(p.relative_to(R)),sha256=sha(p),nonApplicableReason='EXPLICIT_PHYSICAL_BOOTSTRAP_MODULE_AND_COMPLETE_TARGET_SOURCEFILE'))
p=B/'input/512_outbox_eight_byte_reuse_scope.json';v=load(p);targets=set(v['selectedPhysicalNames']);assert len(targets)==8 and all(idx[k]['path'].startswith('src/schubert-nk-api/') for k in targets) and {k for k,x in idx.items() if x['path'] in v['currentSourceFiles']}==targets;cross.append(dict(scope=str(p.relative_to(R)),sha256=sha(p),nonApplicableReason='EXPLICIT_API_MODULE_EIGHT_COMPLETE_SOURCEFILES'))
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),status='PASSIVE_CANDIDATE_GRAPH_INDEPENDENT_METADATA_ONLY',producer=dict(path=str((I/'manifest.json').relative_to(R)),sha256=sha(I/'manifest.json')),currentCoreMain=m['currentCoreMain'],physicalMembersRead=946,sourceClosures=676,statusCounts=m['sourceStatusCounts'],metadataNegativeChecks=negative,crossExpansion=cross,bugs=['BUG-2496'],horizontal=['YKT-2234'],productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,compilerOrJvmExecuted=False,heldMemberBytesRead=False,protectedPathsRead=False,executionAuthorized=False,referenceGraphNotCompleteCallOrTypeGraph=True,whole451Accepted=False,coverageMeasured=False,newAcceptance=0,formalUpdated=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,physical=946,sources=676,metadataNegatives=negative,finiteCrossTargets=3,manifestSha256=sha(O/'manifest.json'))))
