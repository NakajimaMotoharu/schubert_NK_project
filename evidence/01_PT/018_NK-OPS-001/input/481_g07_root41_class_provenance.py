"""Root typed public class digests; existing owned normal/static bytes only, never initialize."""
from pathlib import Path
from collections import Counter
from contextlib import ExitStack
import json,hashlib,re,datetime,zipfile,struct
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/480_g07_root41_class_scope.json';O=B/'evidence/PG23606-g07-root41-class-provenance-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);cfg=load(C)
def class_name(raw):
 assert raw[:4]==b'\xca\xfe\xba\xbe' and int.from_bytes(raw[6:8],'big')==69;p=10;pool={};i=1
 while i<int.from_bytes(raw[8:10],'big'):
  tag=raw[p];p+=1
  if tag==1:n=int.from_bytes(raw[p:p+2],'big');p+=2;pool[i]=raw[p:p+n];p+=n
  elif tag in (7,8,16,19,20):pool[i]=int.from_bytes(raw[p:p+2],'big');p+=2
  elif tag in (3,4,9,10,11,12,17,18):p+=4
  elif tag in (5,6):p+=8;i+=1
  elif tag==15:p+=3
  else:raise AssertionError('bad class metadata')
  i+=1
 return pool[pool[int.from_bytes(raw[p+2:p+4],'big')]].decode()
assert not O.exists() and len(cfg['inputFiles'])==41;prev=R/cfg['previousUpdateManifest'];assert sha(prev)==cfg['previousUpdateManifestSha256'];pm=load(prev);refs=[*pm['priorUpdateRefs'],dict(path=str(prev.with_name('updates.json').relative_to(R)),sha256=pm['updatesSha256'])];prior=[]
for ref in refs:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==132;origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493 and sum((original-old).values())==4361;normal=Path(cfg['normalManifest']);assert sha(normal)==cfg['normalManifestSha256'];nm=load(normal);assert nm['source']==cfg['normalSource'] and nm['actualExit']==0 and set(nm['jars'])=={'api','web','protocol','storage','bootstrap','batch'};assert all(sha(Path(v['path']))==v['sha256'] for v in nm['jars'].values());sp=Path(cfg['staticManifest']);assert sha(sp)==cfg['staticManifestSha256'];sm=load(sp);assert sm['actualExit']==0 and sm['productClassesInitialized']==[] and not sm['javaMainOrTestExecuted'];static={}
for entry in cfg['staticTargetClassEntries']:
 raw=(sp.parent/'classes'/entry).read_bytes();assert class_name(raw)==entry[:-6];static['api:'+entry]=hashlib.sha256(raw).hexdigest()
rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);updates=[];kept=[];typed=0;cache={};kinds=Counter();sources=Counter()
with ExitStack() as stack:
 jars={n:stack.enter_context(zipfile.ZipFile(v['path'])) for n,v in nm['jars'].items()};members={n:set(v.namelist()) for n,v in jars.items()}
 for path,pin in cfg['inputFiles'].items():
  assert re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG[0-9]+-[A-Za-z0-9-]+/qualification\.json',path) and not any(t in path for t in cfg['protectedNameTokens']);p=R/path;assert p.stat().st_size<5000000 and sha(p)==pin;text=p.read_text();obj=load(p);mapping=obj.get('allPhysicalMainSha256');lines=text.splitlines(keepends=True);starts=list(re.finditer(r'^  "allPhysicalMainSha256": ',text,re.M));bounds=None
  if isinstance(mapping,dict) and len(starts)==1:
   at=starts[0].end();value,end=json.JSONDecoder().raw_decode(text,at)
   if value==mapping:bounds=(at,end);typed+=1
  for f in [v for v in rows if v['path']==path and not old[key(v)]]:
   assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']};a=sum(map(len,lines[:f['startLine']-1]));z=sum(map(len,lines[:f['endLine']]));line=''.join(lines[f['startLine']-1:f['endLine']]);pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line)
   if bounds is None or f['startLine']!=f['endLine'] or not bounds[0]<=a<z<=bounds[1]+1 or pair is None:kept.append(dict(**base,status='UNKNOWN_OUTSIDE_ROOT_TYPED_CLASS_SCALAR'));continue
   token=json.loads(pair[1]);value=pair[2];assert mapping.get(token)==value
   if any(v.lower() in token.lower() for v in cfg['protectedNameTokens']):kept.append(dict(**base,status='PROTECTED_NAME_NO_MEMBER_IO'));continue
   parsed=re.fullmatch(r'(api|web|protocol|storage|bootstrap|batch):(dev/codex/schubert/nk/[A-Za-z0-9_$/]+\.class)',token)
   if parsed is None or '..' in token:kept.append(dict(**base,status='UNKNOWN_MAIN_MEMBER_KEY'));continue
   module,entry=parsed.groups();lo=max(0,f['startLine']-2);window=''.join(lines[lo:min(len(lines),f['endLine']+1)]);captures={v[1] for v in rx.finditer(window) if f['startLine']<=lo+window[:v.start(1)].count('\n')+1<=lo+window[:v.end(1)].count('\n')+1<=f['endLine']};assert captures=={value};kind=None
   if entry in members[module]:
    if token not in cache:
     raw=jars[module].read(entry);assert class_name(raw)==entry[:-6];cache[token]=hashlib.sha256(raw).hexdigest()
    if cache[token]==value:kind='CURRENT_NORMAL_MEMBER_BYTE'
   if kind is None and static.get(token)==value:kind='EXISTING_TWO_WHOLE_SOURCE_STATIC_CLASS_BYTE'
   if kind is None:kept.append(dict(**base,status='UNKNOWN_PUBLIC_CLASS_BYTES_MISMATCH_OR_ABSENT'));continue
   updates.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_PUBLIC_CODE_CLASS_DIGEST',fieldRole='allPhysicalMainSha256',normalModule=module,classEntry=entry,internalBinaryName=entry[:-6],artifactProvenanceKind=kind,normalCompileManifestSha256=sha(normal) if kind=='CURRENT_NORMAL_MEMBER_BYTE' else None,normalJarSha256=nm['jars'][module]['sha256'] if kind=='CURRENT_NORMAL_MEMBER_BYTE' else None,staticCompilerManifestSha256=sha(sp) if kind!='CURRENT_NORMAL_MEMBER_BYTE' else None,exactCaptureCount=1,wholeExactCapturePubliclyDerived=True,actualClassByteHashMatched=True,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,capturedValueWritten=False,captureValueHashWritten=False));kinds[kind]+=1;sources[path]+=1
new=Counter(map(key,updates));assert not new.keys()&old.keys() and all(v==original[k]==1 for k,v in new.items());assert Counter(map(key,updates+kept))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);remaining=sum((original-old-new).values());assert remaining==4361-len(updates);statuses=dict(Counter(v['status'] for v in kept));O.mkdir();write(O/'updates.json',updates);write(O/'retained.json',kept);out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=refs,inputFiles=cfg['inputFiles'],normalManifest=dict(path=str(normal),sha256=sha(normal)),normalCoreSource=nm['source'],staticManifest=dict(path=str(sp),sha256=sha(sp)),typedRootMapFiles=typed,candidateRows=len(updates)+len(kept),actualDistinctNormalMemberReads=len(cache),provenanceKindCounts=dict(kinds),sourceCountsWithNewProofs=dict(sources),newFalsePositives=len(updates),remainingUnclassified=remaining,retainedStatusCounts=statuses,updatesSha256=sha(O/'updates.json'),retainedSha256=sha(O/'retained.json'),actualSecretCount=None,binaryOrContainerLimited=22,productTestsExecuted=0,productClassesInitialized=0,heldFourInitializations=0,newCompilerExecutions=0,actualBackendActions=0,originalProducerOrScannerExecuted=False,javaMainOrTestExecuted=False,privateRawOrRuntimeArchiveRead=False,jarMembersExtractedToFilesystem=False,capturedValuesWritten=False,captureValueHashesWritten=False,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,typedFiles=typed,rows=out['candidateRows'],newFalsePositives=len(updates),remaining=remaining,kinds=dict(kinds),status=statuses,manifestSha256=sha(O/'manifest.json'))))
