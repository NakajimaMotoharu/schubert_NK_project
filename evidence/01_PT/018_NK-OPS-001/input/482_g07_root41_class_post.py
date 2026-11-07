"""Independent root-map/class metadata proof, never initializes/invokes target classes."""
from pathlib import Path
from collections import Counter
from contextlib import ExitStack
import json,hashlib,re,datetime,struct,copy,zipfile
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG23606-g07-root41-class-provenance-v1';O=B/'evidence/PG23608-g07-root41-class-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256'])
def binary_name(raw):
 assert raw[:4]==bytes.fromhex('cafebabe') and struct.unpack_from('>H',raw,6)[0]==69;n=struct.unpack_from('>H',raw,8)[0];a=10;i=1;utf={};classes={}
 while i<n:
  tag=raw[a];a+=1
  if tag==1:size=struct.unpack_from('>H',raw,a)[0];a+=2;utf[i]=raw[a:a+size];a+=size
  elif tag==7:classes[i]=struct.unpack_from('>H',raw,a)[0];a+=2
  elif tag in (8,16,19,20):a+=2
  elif tag in (3,4,9,10,11,12,17,18):a+=4
  elif tag in (5,6):a+=8;i+=1
  elif tag==15:a+=3
  else:raise AssertionError('invalid passive class tag')
  i+=1
 return utf[classes[struct.unpack_from('>H',raw,a+2)[0]]].decode()
assert not O.exists();mp=S/'manifest.json';assert sha(mp)=='f79edd24c0c8dd92a7146bfa4be8cf70555507a1d546ecf024dbc738def950bd';m=load(mp);assert m['actualExit']==0;cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp);assert len(cfg['inputFiles'])==41 and m['inputFiles']==cfg['inputFiles'];normal=Path(cfg['normalManifest']);assert sha(normal)==cfg['normalManifestSha256'];nm=load(normal);assert nm['source']==cfg['normalSource'] and nm['actualExit']==0;assert all(sha(Path(v['path']))==v['sha256'] for v in nm['jars'].values());sp=Path(cfg['staticManifest']);assert sha(sp)==cfg['staticManifestSha256'];sm=load(sp);assert sm['actualExit']==0 and sm['productClassesInitialized']==[] and not sm['javaMainOrTestExecuted'];agg=hashlib.sha256()
for p in sorted((sp.parent/'classes').rglob('*.class')):
 raw=p.read_bytes();name=str(p.relative_to(sp.parent/'classes')).encode();agg.update(len(name).to_bytes(8,'big')+name+len(raw).to_bytes(8,'big')+raw)
assert agg.hexdigest()==sm['wholeCompilerOutputAggregateSha256'];statics={}
for entry in cfg['staticTargetClassEntries']:
 raw=(sp.parent/'classes'/entry).read_bytes();assert binary_name(raw)==entry[:-6];statics['api:'+entry]=hashlib.sha256(raw).hexdigest()
origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493;prior=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==132 and sum((original-old).values())==4361;rp=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rp)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rp)['rules']['generic-api-key']['regex'],re.ASCII);expected=[];retained=[];typed=0;cache={};kindcounts=Counter();sourcecounts=Counter()
with ExitStack() as context:
 jars={n:context.enter_context(zipfile.ZipFile(v['path'])) for n,v in nm['jars'].items()};members={n:set(z.namelist()) for n,z in jars.items()}
 for path,pin in cfg['inputFiles'].items():
  assert re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG[0-9]+-[A-Za-z0-9-]+/qualification\.json',path) and not any(t in path for t in cfg['protectedNameTokens']);p=R/path;assert sha(p)==pin;text=p.read_text();data=load(p);mapping=data.get('allPhysicalMainSha256');lines=text.splitlines(keepends=True);begins=[i for i,s in enumerate(lines,1) if s=='  "allPhysicalMainSha256": {\n'];lo=hi=None
  if isinstance(mapping,dict) and len(begins)==1:lo=begins[0];hi=next(i for i,s in enumerate(lines[lo:],lo+1) if s=='  },\n');typed+=1
  for f in [v for v in rows if v['path']==path and not old[key(v)]]:
   assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']};line=''.join(lines[f['startLine']-1:f['endLine']]);pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line)
   if lo is None or f['startLine']!=f['endLine'] or not lo<f['startLine']<hi or pair is None:retained.append(dict(**base,status='UNKNOWN_OUTSIDE_ROOT_TYPED_CLASS_SCALAR'));continue
   token=json.loads(pair[1]);value=pair[2];assert mapping.get(token)==value
   if any(t.lower() in token.lower() for t in cfg['protectedNameTokens']):retained.append(dict(**base,status='PROTECTED_NAME_NO_MEMBER_IO'));continue
   parts=token.split(':',1)
   if len(parts)!=2 or parts[0] not in jars or not re.fullmatch(r'dev/codex/schubert/nk/[A-Za-z0-9_$/]+\.class',parts[1]) or '..' in token:retained.append(dict(**base,status='UNKNOWN_MAIN_MEMBER_KEY'));continue
   module,entry=parts;begin=max(0,f['startLine']-2);win=''.join(lines[begin:min(len(lines),f['endLine']+1)]);cap=set()
   for match in rx.finditer(win):
    first=begin+win[:match.start(1)].count('\n')+1;last=begin+win[:match.end(1)].count('\n')+1
    if f['startLine']<=first<=last<=f['endLine']:cap.add(match[1])
   assert cap=={value};kind=None
   if entry in members[module]:
    if token not in cache:
     raw=jars[module].read(entry);assert binary_name(raw)==entry[:-6];cache[token]=hashlib.sha256(raw).hexdigest()
    if cache[token]==value:kind='CURRENT_NORMAL_MEMBER_BYTE'
   if kind is None and statics.get(token)==value:kind='EXISTING_TWO_WHOLE_SOURCE_STATIC_CLASS_BYTE'
   if kind is None:retained.append(dict(**base,status='UNKNOWN_PUBLIC_CLASS_BYTES_MISMATCH_OR_ABSENT'));continue
   expected.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_PUBLIC_CODE_CLASS_DIGEST',fieldRole='allPhysicalMainSha256',normalModule=module,classEntry=entry,internalBinaryName=entry[:-6],artifactProvenanceKind=kind,normalCompileManifestSha256=sha(normal) if kind=='CURRENT_NORMAL_MEMBER_BYTE' else None,normalJarSha256=nm['jars'][module]['sha256'] if kind=='CURRENT_NORMAL_MEMBER_BYTE' else None,staticCompilerManifestSha256=sha(sp) if kind!='CURRENT_NORMAL_MEMBER_BYTE' else None,exactCaptureCount=1,wholeExactCapturePubliclyDerived=True,actualClassByteHashMatched=True,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,capturedValueWritten=False,captureValueHashWritten=False));kindcounts[kind]+=1;sourcecounts[path]+=1
assert sha(S/'updates.json')==m['updatesSha256'] and sha(S/'retained.json')==m['retainedSha256'];assert load(S/'updates.json')==expected and load(S/'retained.json')==retained;new=Counter(map(key,expected));assert not old.keys()&new.keys() and all(v==original[k]==1 for k,v in new.items());assert Counter(map(key,expected+retained))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);remaining=sum((original-old-new).values());assert len(expected)==m['newFalsePositives']==58 and remaining==m['remainingUnclassified']==4303 and typed==m['typedRootMapFiles']==41 and len(expected)+len(retained)==m['candidateRows']==1501;assert dict(kindcounts)==m['provenanceKindCounts'] and dict(sourcecounts)==m['sourceCountsWithNewProofs'] and len(cache)==m['actualDistinctNormalMemberReads'];statuses=dict(Counter(v['status'] for v in retained));assert statuses==m['retainedStatusCounts'];assert sha(R/m['tool']['path'])==m['tool']['sha256']
def contract(v):
 assert v['newFalsePositives']==58 and v['remainingUnclassified']==4303 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['productTestsExecuted']==v['productClassesInitialized']==v['heldFourInitializations']==v['newCompilerExecutions']==v['actualBackendActions']==v['newAcceptance']==0 and all(v[n] is False for n in ['originalProducerOrScannerExecuted','javaMainOrTestExecuted','privateRawOrRuntimeArchiveRead','jarMembersExtractedToFilesystem','capturedValuesWritten','captureValueHashesWritten','oldOrCurrentRunQualified','wholeSourceIdentityQualified','wholeG07Accepted','whole451Accepted'])
contract(m);checks=0
for n,val in [('newFalsePositives',59),('remainingUnclassified',0),('actualSecretCount',0),('productClassesInitialized',1),('newCompilerExecutions',1),('heldFourInitializations',1),('javaMainOrTestExecuted',True),('privateRawOrRuntimeArchiveRead',True),('jarMembersExtractedToFilesystem',True),('oldOrCurrentRunQualified',True),('wholeSourceIdentityQualified',True),('wholeG07Accepted',True),('whole451Accepted',True)]:
 bad=copy.deepcopy(m);bad[n]=val
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false metadata-to-runtime qualification')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=m['priorUpdateRefs'],updates=dict(path=str((S/'updates.json').relative_to(R)),sha256=sha(S/'updates.json')),typedRootMapFiles=41,inputFiles=cfg['inputFiles'],candidateRows=1501,newFalsePositives=58,remainingUnclassified=4303,actualSecretCount=None,binaryOrContainerLimited=22,provenanceKindCounts=dict(kindcounts),independentNormalMemberReads=len(cache),independentExistingStaticClassReads=2,retainedStatusCounts=statuses,metadataNegativeChecks=checks,productTestsExecuted=0,productClassesInitialized=0,heldFourInitializations=0,newCompilerExecutions=0,actualBackendActions=0,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,newFalsePositives=58,remaining=4303,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
