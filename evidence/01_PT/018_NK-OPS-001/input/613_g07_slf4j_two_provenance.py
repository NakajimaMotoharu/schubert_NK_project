"""One exact existing SDK JAR are opaque public code artifact data; never load/execute."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime,stat
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/611_g07_slf4j_two_scope.json';O=B/'evidence/PG24002-g07-slf4j-two-provenance-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);cfg=load(C);assert not O.exists();assert len(cfg['sdkAllowlist'])==1;prev=R/cfg['previousUpdateManifest'];assert sha(prev)==cfg['previousUpdateManifestSha256'];pm=load(prev);refs=[*pm['priorUpdateRefs'],dict(path=str(prev.with_name('updates.json').relative_to(R)),sha256=pm['updatesSha256'])];prior=[]
for ref in refs:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==1178;origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493 and sum((original-old).values())==3315;rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);updates=[];kept=[];cache={};inventory={};typed=0;roleCounts=Counter();repo=Path(cfg['sdkRepository'])
for path,pin in cfg['inputFiles'].items():
 assert re.fullmatch(cfg['metadataPathRegex'],path) and not re.search(r'(?i)(raw|gitleaks|capture|secret|scan)',path);p=R/path;assert p.stat().st_size<5000000 and sha(p)==pin;text=p.read_text();obj=load(p);lines=text.splitlines(keepends=True);maps=[]
 for role in cfg['fieldRoles']:
  mapping=obj
  for name in role:mapping=mapping.get(name) if isinstance(mapping,dict) else None
  if not isinstance(mapping,dict):continue
  parent=(0,len(text))
  if len(role)==2:
   parents=list(re.finditer(r'^  '+re.escape(json.dumps(role[0]))+': ',text,re.M))
   if len(parents)!=1:continue
   at=parents[0].end();value,end=json.JSONDecoder().raw_decode(text,at)
   if value!=obj[role[0]]:continue
   parent=(at,end)
  marker=r'^'+' '*(2*len(role))+'"'+re.escape(role[-1])+'": ';found=[m for m in re.finditer(marker,text,re.M) if parent[0]<=m.start()<parent[1]]
  if len(found)!=1:continue
  at=found[0].end();decoded,end=json.JSONDecoder().raw_decode(text,at)
  if decoded!=mapping:continue
  maps.append((at,end,mapping,'.'.join(role)));typed+=1
 for f in [v for v in rows if v['path']==path and not old[key(v)]]:
  assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']}
  if f['ruleId']!='generic-api-key' or f['shape']!='ALL_HEX64' or f['startLine']!=f['endLine']:kept.append(dict(**base,status='UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE'));continue
  a=sum(map(len,lines[:f['startLine']-1]));z=sum(map(len,lines[:f['endLine']]));pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',lines[f['startLine']-1]);selected=[v for v in maps if v[0]<=a<z<=v[1]+1]
  if pair is None or len(selected)!=1:kept.append(dict(**base,status='UNKNOWN_OUTSIDE_TYPED_DEPENDENCY_MAP'));continue
  n=json.loads(pair[1]);value=pair[2];assert selected[0][2].get(n)==value
  if n not in cfg['sdkAllowlist'] or any(t.lower() in n.lower() for t in cfg['protectedNameTokens']):kept.append(dict(**base,status='NON_ALLOWLISTED_ARTIFACT_EXCLUDED_BEFORE_IO'));continue
  lo=max(0,f['startLine']-2);win=''.join(lines[lo:min(len(lines),f['endLine']+1)]);cap={m[1] for m in rx.finditer(win) if f['startLine']<=lo+win[:m.start(1)].count('\n')+1<=lo+win[:m.end(1)].count('\n')+1<=f['endLine']};assert cap=={value}
  if n not in cache:
   jar=Path(n);assert jar.is_relative_to(repo) and '..' not in jar.parts;g=cfg['sdkAllowlist'][n];assert jar==repo/g['groupId'].replace('.','/')/g['artifactId']/g['version']/(g['artifactId']+'-'+g['version']+'.jar')
   if not jar.exists() or jar.is_symlink() or jar.resolve()!=jar or not stat.S_ISREG(jar.stat().st_mode):cache[n]=None
   else:
    raw=jar.read_bytes();assert raw[:4]==b'PK\x03\x04';cache[n]=hashlib.sha256(raw).hexdigest();inventory[n]=dict(coordinate=g,bytes=len(raw),zipSignatureVerified=True,regularContainedNonSymlink=True)
  if cache[n] is None or cache[n]!=value:kept.append(dict(**base,status='UNKNOWN_SDK_MISSING_OR_BYTE_MISMATCH'));continue
  updates.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_PUBLIC_SDK_JAR_BYTE_DIGEST',fieldRole=selected[0][3],sdkPath=n,mavenCoordinate=cfg['sdkAllowlist'][n],actualSdkJarByteHashMatched=True,wholeExactCapturePubliclyDerived=True,exactCaptureCount=1,artifactReadOnly=True,artifactLoadedOrExecuted=False,oldOrCurrentRunQualified=False,capturedValueWritten=False,captureValueHashWritten=False));roleCounts[selected[0][3]]+=1
new=Counter(map(key,updates));assert not new.keys()&old.keys() and all(v==original[k]==1 for k,v in new.items());assert Counter(map(key,updates+kept))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);remaining=sum((original-old-new).values());assert remaining==3315-len(updates);agg=hashlib.sha256()
for n in sorted(inventory):
 raw=Path(n).read_bytes();assert hashlib.sha256(raw).hexdigest()==cache[n];label=n.encode();agg.update(len(label).to_bytes(8,'big')+label+len(raw).to_bytes(8,'big')+raw)
O.mkdir();write(O/'updates.json',updates);write(O/'retained.json',kept);out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],config=dict(path=str(C.relative_to(R)),sha256=sha(C)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=refs,inputFiles=cfg['inputFiles'],typedDependencyMaps=typed,candidateRows=len(updates)+len(kept),actualDistinctSdkArtifactsRead=len(inventory),sdkArtifactReadset=inventory,sdkReadsetAggregateSha256=agg.hexdigest(),provenanceRoleCounts=dict(roleCounts),newFalsePositives=len(updates),remainingUnclassified=remaining,retainedStatusCounts=dict(Counter(v['status'] for v in kept)),updatesSha256=sha(O/'updates.json'),retainedSha256=sha(O/'retained.json'),actualSecretCount=None,binaryOrContainerLimited=22,productTestsExecuted=0,productClassesInitialized=0,heldFourInitializations=0,newCompilerExecutions=0,actualBackendActions=0,artifactLoadedOrExecuted=False,downloadOrMavenExecuted=False,originalProducerOrScannerExecuted=False,javaMainOrTestExecuted=False,privateRawOrRuntimeArchiveRead=False,oldProductJarRead=False,nonAllowlistedArtifactIo=False,capturedValuesWritten=False,captureValueHashesWritten=False,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,inputFiles=len(cfg['inputFiles']),sdkArtifacts=len(inventory),newFalsePositives=len(updates),remaining=remaining,statuses=out['retainedStatusCounts'],manifestSha256=sha(O/'manifest.json'))))
