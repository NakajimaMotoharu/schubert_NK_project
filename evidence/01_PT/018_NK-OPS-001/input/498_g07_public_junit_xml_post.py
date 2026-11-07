"""Independent tracked public XML stream-digest/role proof; no report regeneration or tests."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,re,datetime,stat,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG23638-g07-public-junit-xml-provenance-v1';O=B/'evidence/PG23640-g07-public-junit-xml-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);assert not O.exists();mp=S/'manifest.json';assert sha(mp)=='09f548248a7c20932d3376ad14c30a57ef8f4c4344f24a12a119375f03fda831';m=load(mp);cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp);assert len(cfg['inputFiles'])==43 and len(cfg['publicXmlArtifacts'])==1840;origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493;prior=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==893 and sum((original-old).values())==3600;inventory={};index=defaultdict(dict);total=0;aggregate=hashlib.sha256();excluded={}
for n,pin in sorted(cfg['publicXmlArtifacts'].items()):
 assert n.startswith('evidence/01_PT/') and n.endswith('.xml') and Path(n).name.startswith('TEST-') and '..' not in Path(n).parts and not re.search(cfg['xmlDenyRegex'],n);p=R/n
 if not p.exists() or p.is_symlink() or p.resolve()!=p or not stat.S_ISREG(p.stat().st_mode):excluded[n]='UNAVAILABLE_OR_NOT_REGULAR_CONTAINED';continue
 size=p.stat().st_size
 if size>cfg['maximumXmlBytes'] or total+size>cfg['maximumTotalXmlBytes']:excluded[n]='EXPLICIT_BYTE_BUDGET';continue
 label=n.encode();aggregate.update(len(label).to_bytes(8,'big'));aggregate.update(label);aggregate.update(size.to_bytes(8,'big'));h=hashlib.sha256();blob=hashlib.sha1(b'blob '+str(size).encode()+b'\0');count=0
 with p.open('rb') as stream:
  first=stream.read(1024);assert b'<testsuite' in first or b'<testsuites' in first;stream.seek(0)
  while part:=stream.read(65536):h.update(part);blob.update(part);aggregate.update(part);count+=len(part)
 assert count==size and blob.hexdigest()==pin['gitBlobId'];index[Path(n).name].setdefault(h.hexdigest(),n);inventory[n]=dict(gitBlobId=pin['gitBlobId'],mode=pin['mode'],bytes=size,xmlHeaderVerified=True);total+=size
assert inventory==load(S/'public-artifact-readset.json') and sha(S/'public-artifact-readset.json')==m['publicArtifactReadsetSha256'];assert len(inventory)==m['publicXmlArtifactsRead']==1840 and total==m['publicXmlBytesRead']==3488504 and aggregate.hexdigest()==m['publicArtifactAggregateSha256'] and excluded==m['excludedArtifacts'];rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);expected=[];kept=[];typed=0
def bounds(lines,data,role):
 low=0;high=len(lines)+1;value=data
 for depth,name in enumerate(role,1):
  if not isinstance(value,dict) or name not in value:return None
  value=value[name];indent=' '*(depth*2);starts=[i for i,s in enumerate(lines,1) if low<i<high and s==indent+'"'+name+'": {\n']
  if len(starts)!=1:return None
  low=starts[0];high=next(i for i,s in enumerate(lines[low:],low+1) if s in [indent+'},\n',indent+'}\n'])
 return low,high,value
for path,pin in cfg['inputFiles'].items():
 assert re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG[0-9]+-[A-Za-z0-9-]+/qualification\.json',path);p=R/path;assert sha(p)==pin;data=load(p);lines=p.read_text().splitlines(keepends=True);maps=[]
 for prefix in cfg['allowedRootPrefixes']:
  for module in cfg['modules']:
   role=[*prefix,'modules',module,'xmlHashes'];span=bounds(lines,data,role)
   if span and isinstance(span[2],dict):maps.append((*span,module,'.'.join(role)));typed+=1
 for f in [v for v in rows if v['path']==path and not old[key(v)]]:
  assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']}
  if f['ruleId']!='generic-api-key' or f['shape']!='ALL_HEX64' or f['startLine']!=f['endLine']:kept.append(dict(**base,status='UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE'));continue
  pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',lines[f['startLine']-1]);selected=[v for v in maps if v[0]<f['startLine']<v[1]]
  if pair is None or len(selected)!=1:kept.append(dict(**base,status='UNKNOWN_OUTSIDE_TYPED_JUNIT_XML_MAP'));continue
  n=json.loads(pair[1]);value=pair[2];assert selected[0][2].get(n)==value
  if not re.fullmatch(r'TEST-[A-Za-z0-9_.$-]+\.xml',n) or re.search(cfg['xmlDenyRegex'],n):kept.append(dict(**base,status='XML_NAME_EXCLUDED_BEFORE_IO'));continue
  first=max(0,f['startLine']-2);win=''.join(lines[first:min(len(lines),f['endLine']+1)]);cap=set()
  for match in rx.finditer(win):
   a=first+win[:match.start(1)].count('\n')+1;z=first+win[:match.end(1)].count('\n')+1
   if f['startLine']<=a<=z<=f['endLine']:cap.add(match[1])
  assert cap=={value};artifact=index.get(n,{}).get(value)
  if artifact is None:kept.append(dict(**base,status='UNKNOWN_NO_EXACT_TRACKED_PUBLIC_XML_ARTIFACT'));continue
  expected.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_TRACKED_PUBLIC_XML_ARTIFACT_DIGEST',fieldRole=selected[0][4],recordedModule=selected[0][3],xmlBasename=n,publicArtifactPath=artifact,publicGitBlobId=inventory[artifact]['gitBlobId'],artifactByteLength=inventory[artifact]['bytes'],actualPublicArtifactByteHashMatched=True,wholeExactCapturePubliclyDerived=True,exactCaptureCount=1,artifactReadOnly=True,artifactRegenerated=False,testsExecutedOrResultsRequalified=False,oldOrCurrentRunQualified=False,capturedValueWritten=False,captureValueHashWritten=False))
assert typed==m['typedXmlHashMaps'];assert sha(S/'updates.json')==m['updatesSha256'] and sha(S/'retained.json')==m['retainedSha256'];assert load(S/'updates.json')==expected==[] and load(S/'retained.json')==kept;assert Counter(map(key,expected+kept))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);assert len(kept)==m['candidateRows']==1533;assert dict(Counter(v['status'] for v in kept))==m['retainedStatusCounts'];assert sha(R/m['tool']['path'])==m['tool']['sha256']
def contract(v):
 assert v['actualExit']==0 and v['newFalsePositives']==0 and v['remainingUnclassified']==3600 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['productTestsExecuted']==v['productClassesInitialized']==v['heldFourInitializations']==v['newCompilerExecutions']==v['actualBackendActions']==v['newAcceptance']==0 and all(v[n] is False for n in ['originalProducerOrScannerExecuted','artifactRegenerated','javaMainOrTestExecuted','privateRawOrRuntimeArchiveRead','capturedValuesWritten','captureValueHashesWritten','protectedOrDeniedArtifactIo','oldOrCurrentRunQualified','wholeSourceIdentityQualified','wholeG07Accepted','whole451Accepted'])
contract(m);checks=0
for n,v in [('newFalsePositives',1),('actualSecretCount',0),('artifactRegenerated',True),('javaMainOrTestExecuted',True),('privateRawOrRuntimeArchiveRead',True),('protectedOrDeniedArtifactIo',True),('productClassesInitialized',1),('oldOrCurrentRunQualified',True),('wholeG07Accepted',True),('whole451Accepted',True)]:
 bad=copy.deepcopy(m);bad[n]=v
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false XML artifact credit')
for n in ['TEST-RootFailedStartRecoveryTest.xml','TEST-RootFailedStartPairRecoveryTest.xml','TEST-WebNativeCodecsTest.xml','evidence/private/TEST-x.xml']:
 assert re.search(cfg['xmlDenyRegex'],n);checks+=1
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),inputFiles=cfg['inputFiles'],candidateRows=1533,newFalsePositives=0,remainingUnclassified=3600,actualSecretCount=None,binaryOrContainerLimited=22,independentlyReadPublicXmlArtifacts=1840,publicXmlBytesRead=3488504,publicArtifactAggregateSha256=aggregate.hexdigest(),retainedStatusCounts=m['retainedStatusCounts'],metadataNegativeChecks=checks,productTestsExecuted=0,productClassesInitialized=0,newCompilerExecutions=0,actualBackendActions=0,artifactRegenerated=False,privateRawOrRuntimeArchiveRead=False,oldOrCurrentRunQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,newFalsePositives=0,remaining=3600,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
