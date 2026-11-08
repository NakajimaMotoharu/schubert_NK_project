"""Read normal ClassFile symbols only; a candidate is not execution authority."""
from pathlib import Path
import json,hashlib,datetime,zipfile,collections,re
from class_reference_metadata import read,source_closure
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/521_ordinary_reference_candidate_scope.json';O=B/'evidence/PG23748-ordinary-reference-candidates-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert not O.exists();cfg=load(C)
for n,pin in cfg['publicInputs'].items():assert sha(R/n)==pin
assert sha(R/cfg['parser']['path'])==cfg['parser']['sha256'];normal=Path(cfg['normalManifest']['path']);assert sha(normal)==cfg['normalManifest']['sha256'];m=load(normal);assert m['actualExit']==0 and m['source']==cfg['currentCoreMain'];idx=load(B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json');selected=set(cfg['selectedPhysicalNames']);heldSources=set(cfg['excludedHeldSources']);assert all(idx[n]['path'] not in heldSources and n not in cfg['excludedHeldFamilies'] for n in selected)
parsed={};jars={}
for module in ['protocol','api','web','storage']:
 p=Path(m['jars'][module]['path']);assert sha(p)==m['jars'][module]['sha256'];jars[module]=m['jars'][module]
 with zipfile.ZipFile(p) as z:
  for n in selected:
   if f'/schubert-nk-{module}/' not in idx[n]['path']:continue
   raw=z.read(n+'.class');assert hashlib.sha256(raw).hexdigest()==idx[n]['sha256'];v=read(raw);assert v['className']==n and v['sourceFile']==Path(idx[n]['path']).name;parsed[n]=v
assert set(parsed)==selected
sources=sorted({idx[n]['path'] for n in selected});physical={s:sorted(n for n in selected if idx[n]['path']==s) for s in sources};direct={s:set() for s in sources};edges={s:set() for s in sources};unresolved={s:set() for s in sources};foreign={s:set() for s in sources}
# Conservative symbol groups mark a review requirement, never an unsafe operation or refusal.
sidePrefixes=('java/lang/foreign/','java/lang/Process','java/io/File','java/io/RandomAccessFile','java/nio/file/','java/nio/channels/','java/net/','javax/net/','java/sql/DriverManager','sun/','jdk/internal/','io/netty/','org/postgresql/')
providedPrefixes=('java/','javax/sql/','javax/crypto/','javax/servlet/','jakarta/jms/','jakarta/servlet/','com/sun/net/httpserver/HttpExchange','com/sun/net/httpserver/HttpHandler','com/sun/net/httpserver/Headers')
for n,v in parsed.items():
 s=idx[n]['path']
 if v['reflectiveOrDynamicLookup']:direct[s].add('DYNAMIC_LOOKUP_REQUIRES_INDIVIDUAL_REVIEW')
 for ref in v['references']:
  if ref in selected:edges[s].add(idx[ref]['path'])
  elif ref.startswith('dev/codex/schubert/'):
   unresolved[s].add(ref);direct[s].add('OUTSIDE_SELECTED_PRODUCT_GRAPH')
  elif ref.startswith(sidePrefixes):foreign[s].add(ref);direct[s].add('EXTERNAL_IO_OR_NATIVE_OR_PROCESS_REFERENCE_REVIEW')
  elif not ref.startswith(providedPrefixes):foreign[s].add(ref);direct[s].add('NON_JDK_SDK_GRAPH_REVIEW_REQUIRED')
  elif ref.startswith(('javax/crypto/','java/security/')):foreign[s].add(ref);direct[s].add('CRYPTOGRAPHIC_PORT_REVIEW_REQUIRED_NO_KEY_OPERATIONS_AUTHORIZED')
markers,unknown=source_closure(direct,edges,unresolved);known=set(cfg['alreadyNamedCandidatePaths']);rows=[]
for s in sources:
 full={n for n,v in idx.items() if v['path']==s};assert full==set(physical[s]);code=any(idx[n]['hasCode'] for n in full);labels=sorted(markers[s]);status='REVIEW_REQUIRED_TRANSITIVE_MARKERS' if labels else 'ALREADY_NAMED_CODE_CANDIDATE_NOT_REQUALIFIED' if s in known else 'NATURAL_NO_CODE_NO_EXECUTION_REQUIRED' if not code else 'NO_MARKED_REFERENCE_NEW_REVIEW_CANDIDATE_NOT_EXECUTION_AUTHORITY';rows.append(dict(mainPath=s,physical=physical[s],hasCode=code,directReviewMarkers=sorted(direct[s]),transitiveReviewMarkers=labels,unresolvedProductReferences=sorted(unknown[s]),foreignReferences=sorted(foreign[s]),sourceEdges=sorted(edges[s]),alreadyNamed=s in known,status=status,executionAuthorized=False))
O.mkdir();write(O/'source-candidates.json',rows);write(O/'physical-symbols.json',parsed);out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),status='PASSIVE_CANDIDATE_GRAPH_COMPLETE_NO_EXECUTION_AUTHORITY',config=dict(path=str(C.relative_to(R)),sha256=sha(C)),currentCoreMain=m['source'],physicalMembersRead=len(parsed),sourceClosures=len(rows),sourceStatusCounts=dict(collections.Counter(x['status'] for x in rows)),normalJars=jars,heldMemberBytesRead=False,protectedPathsRead=False,actualBackendActions=0,productClassesInitialized=0,productTestsExecuted=0,compilerOrJvmExecuted=False,newAcceptance=0,formalUpdated=False,effortRate=None,coverageMeasured=False,whole451Accepted=False,artifacts={p.name:sha(p) for p in O.iterdir()},tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,physical=len(parsed),sources=len(rows),statuses=out['sourceStatusCounts'],manifestSha256=sha(O/'manifest.json'))))
