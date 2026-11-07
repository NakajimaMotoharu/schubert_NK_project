"""Public source-file digest provenance only; no Java/tool/target code execution."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/484_g07_public_source_hash_scope.json';O=B/'evidence/PG23614-g07-public-source-hash-provenance-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);cfg=load(C);assert not O.exists();assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==cfg['currentHead'];prev=R/cfg['previousUpdateManifest'];assert sha(prev)==cfg['previousUpdateManifestSha256'];pm=load(prev);refs=[*pm['priorUpdateRefs'],dict(path=str(prev.with_name('updates.json').relative_to(R)),sha256=pm['updatesSha256'])];prior=[]
for ref in refs:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==190;origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493 and sum((original-old).values())==4303;rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);updates=[];kept=[];cache={};reads=0;typed=0;sourceModes={};roleCounts=Counter()
def eligible(n):return bool(re.fullmatch(cfg['sourcePathRegex'],n)) and '..' not in Path(n).parts and not any(t.lower() in n.lower() for t in cfg['sourceDenyTokens'])
for path,pin in cfg['inputFiles'].items():
 assert re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG[89][0-9]{3}-[A-Za-z0-9-]*host[A-Za-z0-9-]*/manifest\.json',path);p=R/path;assert p.stat().st_size<5000000 and sha(p)==pin;text=p.read_text();obj=load(p);lines=text.splitlines(keepends=True);maps=[]
 for role in cfg['fieldRoles']:
  mapping=obj
  for name in role:mapping=mapping.get(name) if isinstance(mapping,dict) else None
  if not isinstance(mapping,dict):continue
  parentBounds=(0,len(text))
  if len(role)==2:
   parents=list(re.finditer(r'^  "begin": ',text,re.M))
   if len(parents)!=1:continue
   at=parents[0].end();value,end=json.JSONDecoder().raw_decode(text,at)
   if value!=obj['begin']:continue
   parentBounds=(at,end)
  marker=r'^'+' '*(2*len(role))+'"'+re.escape(role[-1])+'": ';found=[m for m in re.finditer(marker,text,re.M) if parentBounds[0]<=m.start()<parentBounds[1]]
  if len(found)!=1:continue
  at=found[0].end();decoded,end=json.JSONDecoder().raw_decode(text,at)
  if decoded!=mapping:continue
  maps.append((at,end,mapping,'.'.join(role)));typed+=1
 for f in [v for v in rows if v['path']==path and not old[key(v)]]:
  assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']}
  if f['ruleId']!='generic-api-key' or f['shape']!='ALL_HEX64' or f['startLine']!=f['endLine']:kept.append(dict(**base,status='UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE'));continue
  a=sum(map(len,lines[:f['startLine']-1]));z=sum(map(len,lines[:f['endLine']]));line=lines[f['startLine']-1];pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line);selected=[m for m in maps if m[0]<=a<z<=m[1]+1]
  if pair is None or len(selected)!=1:kept.append(dict(**base,status='UNKNOWN_OUTSIDE_DECLARED_TYPED_SOURCE_HASH_MAP'));continue
  n=json.loads(pair[1]);value=pair[2];mapping=selected[0][2];assert mapping.get(n)==value
  if not eligible(n):kept.append(dict(**base,status='SOURCE_EXCLUDED_BEFORE_ANY_SOURCE_IO'));continue
  lo=max(0,f['startLine']-2);window=''.join(lines[lo:min(len(lines),f['endLine']+1)]);captures={m[1] for m in rx.finditer(window) if f['startLine']<=lo+window[:m.start(1)].count('\n')+1<=lo+window[:m.end(1)].count('\n')+1<=f['endLine']};assert captures=={value}
  if n not in cache:
   listing=subprocess.check_output(['git','ls-tree','-z',cfg['currentHead'],'--',n],cwd=R)
   if not listing:cache[n]=None
   else:
    header,listed=listing[:-1].split(b'\t',1);mode,kind,oid=header.decode().split();assert listed.decode()==n
    if kind!='blob' or mode not in ['100644','100755'] or (R/n).is_symlink():cache[n]=None
    else:
     raw=(R/n).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid;cache[n]=(hashlib.sha256(raw).hexdigest(),oid,mode);reads+=1;sourceModes[n]=mode
  proof=cache[n]
  if proof is None or proof[0]!=value:kept.append(dict(**base,status='UNKNOWN_CURRENT_TRACKED_SOURCE_MISSING_OR_BYTE_MISMATCH'));continue
  updates.append(dict(**base,disposition='FALSE_POSITIVE_PUBLIC_TRACKED_JAVA_SOURCE_FILE_DIGEST',fieldRole=selected[0][3],sourcePath=n,currentPublicHead=cfg['currentHead'],currentGitBlobId=proof[1],gitMode=proof[2],actualSourceByteHashMatched=True,wholeExactCapturePubliclyDerived=True,exactCaptureCount=1,sourceReadOnly=True,sourceCompiledOrExecuted=False,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,capturedValueWritten=False,captureValueHashWritten=False));roleCounts[selected[0][3]]+=1
new=Counter(map(key,updates));assert not new.keys()&old.keys() and all(v==original[k]==1 for k,v in new.items());assert Counter(map(key,updates+kept))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);remaining=sum((original-old-new).values());assert remaining==4303-len(updates);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==cfg['currentHead'];O.mkdir();write(O/'updates.json',updates);write(O/'retained.json',kept);out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=refs,inputFiles=cfg['inputFiles'],currentPublicHead=cfg['currentHead'],typedSourceHashMaps=typed,candidateRows=len(updates)+len(kept),actualDistinctSourceFilesRead=reads,sourceReadset=list(sourceModes),provenanceRoleCounts=dict(roleCounts),newFalsePositives=len(updates),remainingUnclassified=remaining,retainedStatusCounts=dict(Counter(v['status'] for v in kept)),updatesSha256=sha(O/'updates.json'),retainedSha256=sha(O/'retained.json'),actualSecretCount=None,binaryOrContainerLimited=22,productTestsExecuted=0,productClassesInitialized=0,heldFourInitializations=0,newCompilerExecutions=0,actualBackendActions=0,originalProducerOrScannerExecuted=False,javaMainOrTestExecuted=False,privateRawOrRuntimeArchiveRead=False,capturedValuesWritten=False,captureValueHashesWritten=False,protectedOrDeniedSourceIo=False,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,files=len(cfg['inputFiles']),sourceReads=reads,newFalsePositives=len(updates),remaining=remaining,statuses=out['retainedStatusCounts'],manifestSha256=sha(O/'manifest.json'))))
