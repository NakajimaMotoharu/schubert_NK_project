"""Independent typed dependency role and streaming SDK byte digest oracle; no JAR execution."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime,stat,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG23630-g07-sdk-remaining339-provenance-v1';O=B/'evidence/PG23632-g07-sdk-remaining339-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);assert not O.exists();mp=S/'manifest.json';assert sha(mp)=='476156ab4adbf9c5f27b785babf6d19b0e090006a9b090ba9e416e8a898d2521';m=load(mp);cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp);assert len(cfg['inputFiles'])==339 and len(cfg['sdkAllowlist'])==9;origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493;prior=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==784 and sum((original-old).values())==3709;rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);expected=[];kept=[];typed=0;cache={};inventory={};rolecounts=Counter();repo=Path(cfg['sdkRepository'])
for path,pin in cfg['inputFiles'].items():
 assert re.fullmatch(cfg['metadataPathRegex'],path) and not re.search(r'(?i)(raw|gitleaks|capture|secret|scan)',path);p=R/path;assert sha(p)==pin;data=load(p);lines=p.read_text().splitlines(keepends=True);maps=[]
 for role in cfg['fieldRoles']:
  obj=data
  for n in role:obj=obj.get(n) if isinstance(obj,dict) else None
  if not isinstance(obj,dict):continue
  begin=0;end=len(lines)+1
  if len(role)==2:
   parents=[i for i,s in enumerate(lines,1) if s=='  "begin": {\n']
   if len(parents)!=1:continue
   begin=parents[0];end=next(i for i,s in enumerate(lines[begin:],begin+1) if s in ['  },\n','  }\n'])
  indent=' '*(2*len(role));starts=[i for i,s in enumerate(lines,1) if begin<i<end and s==indent+'"'+role[-1]+'": {\n']
  if len(starts)!=1:continue
  lo=starts[0];hi=next(i for i,s in enumerate(lines[lo:],lo+1) if s in [indent+'},\n',indent+'}\n']);maps.append((lo,hi,obj,'.'.join(role)));typed+=1
 for f in [v for v in rows if v['path']==path and not old[key(v)]]:
  assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']}
  if f['ruleId']!='generic-api-key' or f['shape']!='ALL_HEX64' or f['startLine']!=f['endLine']:kept.append(dict(**base,status='UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE'));continue
  pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',lines[f['startLine']-1]);selected=[v for v in maps if v[0]<f['startLine']<v[1]]
  if pair is None or len(selected)!=1:kept.append(dict(**base,status='UNKNOWN_OUTSIDE_TYPED_DEPENDENCY_MAP'));continue
  n=json.loads(pair[1]);value=pair[2];assert selected[0][2].get(n)==value
  if n not in cfg['sdkAllowlist'] or any(v.lower() in n.lower() for v in cfg['protectedNameTokens']):kept.append(dict(**base,status='NON_ALLOWLISTED_ARTIFACT_EXCLUDED_BEFORE_IO'));continue
  first=max(0,f['startLine']-2);win=''.join(lines[first:min(len(lines),f['endLine']+1)]);cap=set()
  for match in rx.finditer(win):
   a=first+win[:match.start(1)].count('\n')+1;z=first+win[:match.end(1)].count('\n')+1
   if f['startLine']<=a<=z<=f['endLine']:cap.add(match[1])
  assert cap=={value}
  if n not in cache:
   jar=Path(n);g=cfg['sdkAllowlist'][n];assert jar==repo/g['groupId'].replace('.','/')/g['artifactId']/g['version']/(g['artifactId']+'-'+g['version']+'.jar');assert jar.is_relative_to(repo) and '..' not in jar.parts
   if not jar.exists() or jar.is_symlink() or jar.resolve()!=jar or not stat.S_ISREG(jar.stat().st_mode):cache[n]=None
   else:
    with jar.open('rb') as stream:assert stream.read(4)==b'PK\x03\x04';stream.seek(0);digest=hashlib.file_digest(stream,'sha256').hexdigest()
    cache[n]=digest;inventory[n]=dict(coordinate=g,bytes=jar.stat().st_size,zipSignatureVerified=True,regularContainedNonSymlink=True)
  if cache[n] is None or cache[n]!=value:kept.append(dict(**base,status='UNKNOWN_SDK_MISSING_OR_BYTE_MISMATCH'));continue
  expected.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_PUBLIC_SDK_JAR_BYTE_DIGEST',fieldRole=selected[0][3],sdkPath=n,mavenCoordinate=cfg['sdkAllowlist'][n],actualSdkJarByteHashMatched=True,wholeExactCapturePubliclyDerived=True,exactCaptureCount=1,artifactReadOnly=True,artifactLoadedOrExecuted=False,oldOrCurrentRunQualified=False,capturedValueWritten=False,captureValueHashWritten=False));rolecounts[selected[0][3]]+=1
assert sha(S/'updates.json')==m['updatesSha256'] and sha(S/'retained.json')==m['retainedSha256'];assert load(S/'updates.json')==expected and load(S/'retained.json')==kept;new=Counter(map(key,expected));assert not new.keys()&old.keys() and all(v==original[k]==1 for k,v in new.items());assert Counter(map(key,expected+kept))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);remaining=sum((original-old-new).values());assert len(expected)==m['newFalsePositives']==109 and remaining==m['remainingUnclassified']==3600;assert len(expected)+len(kept)==m['candidateRows']==1488 and typed==m['typedDependencyMaps'];assert inventory==m['sdkArtifactReadset'] and len(inventory)==m['actualDistinctSdkArtifactsRead']==9 and dict(rolecounts)==m['provenanceRoleCounts'];assert dict(Counter(v['status'] for v in kept))==m['retainedStatusCounts'];agg=hashlib.sha256()
for n in sorted(inventory):
 label=n.encode();size=inventory[n]['bytes'];agg.update(len(label).to_bytes(8,'big'));agg.update(label);agg.update(size.to_bytes(8,'big'))
 with Path(n).open('rb') as stream:
  while chunk:=stream.read(131072):agg.update(chunk)
assert agg.hexdigest()==m['sdkReadsetAggregateSha256'];assert sha(R/m['tool']['path'])==m['tool']['sha256']
def contract(v):
 assert v['actualExit']==0 and v['newFalsePositives']==109 and v['remainingUnclassified']==3600 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['actualDistinctSdkArtifactsRead']==9 and v['productTestsExecuted']==v['productClassesInitialized']==v['heldFourInitializations']==v['newCompilerExecutions']==v['actualBackendActions']==v['newAcceptance']==0 and all(v[n] is False for n in ['artifactLoadedOrExecuted','downloadOrMavenExecuted','originalProducerOrScannerExecuted','javaMainOrTestExecuted','privateRawOrRuntimeArchiveRead','oldProductJarRead','nonAllowlistedArtifactIo','capturedValuesWritten','captureValueHashesWritten','oldOrCurrentRunQualified','wholeSourceIdentityQualified','wholeG07Accepted','whole451Accepted'])
contract(m);checks=0
for n,v in [('newFalsePositives',110),('actualSecretCount',0),('actualDistinctSdkArtifactsRead',10),('artifactLoadedOrExecuted',True),('downloadOrMavenExecuted',True),('oldProductJarRead',True),('nonAllowlistedArtifactIo',True),('privateRawOrRuntimeArchiveRead',True),('productClassesInitialized',1),('oldOrCurrentRunQualified',True),('wholeG07Accepted',True),('whole451Accepted',True)]:
 bad=copy.deepcopy(m);bad[n]=v
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false SDK provenance credit')
for n in ['/tmp/credential.jar',str(R.parent/'pgpt-runs/PG379/old/snapshot/api.jar'),str(repo/'org/slf4j/slf4j-api/2.0.18/../credential'),str(repo/'new-artifact.jar')]:assert n not in cfg['sdkAllowlist'];checks+=1
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=m['priorUpdateRefs'],updates=dict(path=str((S/'updates.json').relative_to(R)),sha256=sha(S/'updates.json')),inputFiles=cfg['inputFiles'],candidateRows=1488,newFalsePositives=109,remainingUnclassified=3600,actualSecretCount=None,binaryOrContainerLimited=22,independentlyReadSdkArtifacts=9,sdkArtifactReadset=inventory,sdkReadsetAggregateSha256=agg.hexdigest(),retainedStatusCounts=m['retainedStatusCounts'],metadataNegativeChecks=checks,productTestsExecuted=0,productClassesInitialized=0,newCompilerExecutions=0,actualBackendActions=0,artifactLoadedOrExecuted=False,downloadOrMavenExecuted=False,oldProductJarRead=False,nonAllowlistedArtifactIo=False,capturedValuesWritten=False,captureValueHashesWritten=False,oldOrCurrentRunQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,newFalsePositives=109,remaining=remaining,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
