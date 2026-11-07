"""Opaque tracked public XML digest provenance, not JUnit execution or result acceptance."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,re,datetime,subprocess,stat
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/496_g07_public_junit_xml_scope.json';O=B/'evidence/PG23638-g07-public-junit-xml-provenance-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);cfg=load(C);assert not O.exists();assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==cfg['currentHead'];prev=R/cfg['previousUpdateManifest'];assert sha(prev)==cfg['previousUpdateManifestSha256'];pm=load(prev);refs=[*pm['priorUpdateRefs'],dict(path=str(prev.with_name('updates.json').relative_to(R)),sha256=pm['updatesSha256'])];prior=[]
for ref in refs:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==893;origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493 and sum((original-old).values())==3600;index=defaultdict(dict);inventory={};excluded={};aggregate=hashlib.sha256();total=0
for n,pin in sorted(cfg['publicXmlArtifacts'].items()):
 assert n.startswith('evidence/01_PT/') and n.endswith('.xml') and Path(n).name.startswith('TEST-') and '..' not in Path(n).parts and not re.search(cfg['xmlDenyRegex'],n);p=R/n
 if not p.exists() or p.is_symlink() or p.resolve()!=p or not stat.S_ISREG(p.stat().st_mode):excluded[n]='UNAVAILABLE_OR_NOT_REGULAR_CONTAINED';continue
 size=p.stat().st_size
 if size>cfg['maximumXmlBytes'] or total+size>cfg['maximumTotalXmlBytes']:excluded[n]='EXPLICIT_BYTE_BUDGET';continue
 raw=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['gitBlobId'];assert b'<testsuite' in raw[:1024] or b'<testsuites' in raw[:1024];digest=hashlib.sha256(raw).hexdigest();index[Path(n).name].setdefault(digest,n);inventory[n]=dict(gitBlobId=pin['gitBlobId'],mode=pin['mode'],bytes=len(raw),xmlHeaderVerified=True);label=n.encode();aggregate.update(len(label).to_bytes(8,'big')+label+len(raw).to_bytes(8,'big')+raw);total+=len(raw)
rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);updates=[];kept=[];typed=0;modules=Counter()
def typed_span(text,data,role):
 parent=(0,len(text));value=data
 for depth,name in enumerate(role,1):
  if not isinstance(value,dict) or name not in value:return None
  value=value[name];pattern=r'^'+' '*(depth*2)+'"'+re.escape(name)+'": ';hits=[v for v in re.finditer(pattern,text,re.M) if parent[0]<=v.start()<parent[1]]
  if len(hits)!=1:return None
  at=hits[0].end();decoded,end=json.JSONDecoder().raw_decode(text,at)
  if decoded!=value:return None
  parent=(at,end)
 return (*parent,value)
for path,pin in cfg['inputFiles'].items():
 assert re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG[0-9]+-[A-Za-z0-9-]+/qualification\.json',path);p=R/path;assert sha(p)==pin;text=p.read_text();data=load(p);lines=text.splitlines(keepends=True);maps=[]
 for prefix in cfg['allowedRootPrefixes']:
  for module in cfg['modules']:
   role=[*prefix,'modules',module,'xmlHashes'];found=typed_span(text,data,role)
   if found and isinstance(found[2],dict):maps.append((*found,module,'.'.join(role)));typed+=1
 for f in [v for v in rows if v['path']==path and not old[key(v)]]:
  assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']}
  if f['ruleId']!='generic-api-key' or f['shape']!='ALL_HEX64' or f['startLine']!=f['endLine']:kept.append(dict(**base,status='UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE'));continue
  start=sum(map(len,lines[:f['startLine']-1]));stop=sum(map(len,lines[:f['endLine']]));pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',lines[f['startLine']-1]);selected=[v for v in maps if v[0]<=start<stop<=v[1]+1]
  if pair is None or len(selected)!=1:kept.append(dict(**base,status='UNKNOWN_OUTSIDE_TYPED_JUNIT_XML_MAP'));continue
  name=json.loads(pair[1]);value=pair[2];assert selected[0][2].get(name)==value
  if not re.fullmatch(r'TEST-[A-Za-z0-9_.$-]+\.xml',name) or re.search(cfg['xmlDenyRegex'],name):kept.append(dict(**base,status='XML_NAME_EXCLUDED_BEFORE_IO'));continue
  lo=max(0,f['startLine']-2);win=''.join(lines[lo:min(len(lines),f['endLine']+1)]);cap={m[1] for m in rx.finditer(win) if f['startLine']<=lo+win[:m.start(1)].count('\n')+1<=lo+win[:m.end(1)].count('\n')+1<=f['endLine']};assert cap=={value}
  match=index.get(name,{}).get(value)
  if match is None:kept.append(dict(**base,status='UNKNOWN_NO_EXACT_TRACKED_PUBLIC_XML_ARTIFACT'));continue
  updates.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_TRACKED_PUBLIC_XML_ARTIFACT_DIGEST',fieldRole=selected[0][4],recordedModule=selected[0][3],xmlBasename=name,publicArtifactPath=match,publicGitBlobId=inventory[match]['gitBlobId'],artifactByteLength=inventory[match]['bytes'],actualPublicArtifactByteHashMatched=True,wholeExactCapturePubliclyDerived=True,exactCaptureCount=1,artifactReadOnly=True,artifactRegenerated=False,testsExecutedOrResultsRequalified=False,oldOrCurrentRunQualified=False,capturedValueWritten=False,captureValueHashWritten=False));modules[selected[0][3]]+=1
new=Counter(map(key,updates));assert not new.keys()&old.keys() and all(v==original[k]==1 for k,v in new.items());assert Counter(map(key,updates+kept))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);remaining=sum((original-old-new).values());assert remaining==3600-len(updates);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==cfg['currentHead'];O.mkdir();write(O/'updates.json',updates);write(O/'retained.json',kept);write(O/'public-artifact-readset.json',inventory);out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=refs,inputFiles=cfg['inputFiles'],typedXmlHashMaps=typed,candidateRows=len(updates)+len(kept),publicXmlArtifactsRead=len(inventory),publicXmlBytesRead=total,publicArtifactReadsetSha256=sha(O/'public-artifact-readset.json'),publicArtifactAggregateSha256=aggregate.hexdigest(),excludedArtifacts=excluded,provenanceModuleCounts=dict(modules),newFalsePositives=len(updates),remainingUnclassified=remaining,retainedStatusCounts=dict(Counter(v['status'] for v in kept)),updatesSha256=sha(O/'updates.json'),retainedSha256=sha(O/'retained.json'),actualSecretCount=None,binaryOrContainerLimited=22,productTestsExecuted=0,productClassesInitialized=0,heldFourInitializations=0,newCompilerExecutions=0,actualBackendActions=0,originalProducerOrScannerExecuted=False,artifactRegenerated=False,javaMainOrTestExecuted=False,privateRawOrRuntimeArchiveRead=False,capturedValuesWritten=False,captureValueHashesWritten=False,protectedOrDeniedArtifactIo=False,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,xmlArtifacts=len(inventory),xmlBytes=total,newFalsePositives=len(updates),remaining=remaining,statuses=out['retainedStatusCounts'],manifestSha256=sha(O/'manifest.json'))))
