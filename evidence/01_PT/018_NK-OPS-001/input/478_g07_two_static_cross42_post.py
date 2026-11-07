"""Independent line/typed-map and actual static class-byte provenance; no execution."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime,struct,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG23598-g07-two-static-cross42-provenance-v1';O=B/'evidence/PG23600-g07-two-static-cross42-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256'])
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
assert not O.exists();mp=S/'manifest.json';assert sha(mp)=='8fa1d544eb3470c5fcfcc992b8190d4ba1eb4a053ee1a1e72368bfbc1b6d96b0';m=load(mp);assert m['actualExit']==0;cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp);assert len(cfg['inputFiles'])==42 and cfg['inputFiles']==m['inputFiles'];sp=Path(cfg['staticManifest']);assert sha(sp)==cfg['staticManifestSha256']==m['staticCompilerManifest']['sha256'];sm=load(sp);priorp=R/cfg['priorUpdateManifest'];assert sha(priorp)==cfg['priorUpdateManifestSha256'];pm=load(priorp);assert pm['staticCompilerManifest']['sha256']==sha(sp);assert sm['actualExit']==0 and sm['productClassesInitialized']==[];agg=hashlib.sha256()
for p in sorted((sp.parent/'classes').rglob('*.class')):
 raw=p.read_bytes();name=str(p.relative_to(sp.parent/'classes')).encode();agg.update(len(name).to_bytes(8,'big')+name+len(raw).to_bytes(8,'big')+raw)
assert agg.hexdigest()==sm['wholeCompilerOutputAggregateSha256']==pm['compilerOutputAggregateSha256'];target={}
for entry in cfg['targetClassEntries']:
 raw=(sp.parent/'classes'/entry).read_bytes();assert binary_name(raw)==entry[:-6];target['api:'+entry]=hashlib.sha256(raw).hexdigest()
origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);original=Counter(map(key,rows));assert len(rows)==4493;prior=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==130 and sum((original-old).values())==4363;rp=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rp)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rp)['rules']['generic-api-key']['regex'],re.ASCII);expected=[];retained=[];typed=0;status=Counter();groupcounts=Counter()
for path,pin in cfg['inputFiles'].items():
 assert re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG[0-9]+-[A-Za-z0-9-]+/qualification\.json',path) and not any(t in path for t in cfg['protectedNameTokens']);p=R/path;assert sha(p)==pin;text=p.read_text();data=load(p);mapping=data.get('result',{}).get('allPhysicalMainSha256');lines=text.splitlines(keepends=True);starts=[i for i,s in enumerate(lines,1) if s=='    "allPhysicalMainSha256": {\n'];lo=hi=None
 if isinstance(mapping,dict) and len(starts)==1:
  lo=starts[0];hi=next(i for i,s in enumerate(lines[lo:],lo+1) if s=='    },\n');typed+=1
 for f in [v for v in rows if v['path']==path and not old[key(v)]]:
  assert f['inputSha256']==pin;base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']};line=''.join(lines[f['startLine']-1:f['endLine']]);pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line)
  if lo is None or f['startLine']!=f['endLine'] or not lo<f['startLine']<hi or pair is None:retained.append(dict(**base,status='UNKNOWN_OUTSIDE_TYPED_CLASS_SCALAR'));continue
  token=json.loads(pair[1]);value=pair[2];assert mapping.get(token)==value
  if token not in target:retained.append(dict(**base,status='UNKNOWN_OTHER_CLASS_OR_MODULE'));continue
  begin=max(0,f['startLine']-2);win=''.join(lines[begin:min(len(lines),f['endLine']+1)]);cap=set()
  for match in rx.finditer(win):
   first=begin+win[:match.start(1)].count('\n')+1;last=begin+win[:match.end(1)].count('\n')+1
   if f['startLine']<=first<=last<=f['endLine']:cap.add(match[1])
  assert cap=={value}
  if target[token]!=value:retained.append(dict(**base,status='UNKNOWN_STATIC_CLASS_BYTE_MISMATCH'));continue
  expected.append(dict(**base,disposition='FALSE_POSITIVE_EXISTING_STATIC_PUBLIC_WHOLE_SOURCE_CLASS_DIGEST',fieldRole='result.allPhysicalMainSha256',classEntry=token[4:],exactCaptureCount=1,staticCompilerManifestSha256=sha(sp),independentOriginalStaticPostSha256=sha(priorp),historicalPublicSourceUsedForStaticCode=sm['begin']['historicalSource'],wholeExactCapturePubliclyDerived=True,actualExistingStaticClassByteMatched=True,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,capturedValueWritten=False,captureValueHashWritten=False));groupcounts[path]+=1
assert sha(S/'updates.json')==m['updatesSha256'] and sha(S/'retained.json')==m['retainedSha256'];assert load(S/'updates.json')==expected and load(S/'retained.json')==retained;new=Counter(map(key,expected));assert not old.keys()&new.keys() and all(v==original[k]==1 for k,v in new.items());assert Counter(map(key,expected+retained))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);remaining=sum((original-old-new).values());assert len(expected)==2 and remaining==4361 and typed==m['typedMapFiles']==1 and len(expected)+len(retained)==m['candidateRows']==1548 and dict(groupcounts)==m['sourceCountsWithNewProofs']
for v in retained:status[v['status']]+=1
assert dict(status)==m['retainedStatusCounts']
def contract(v):
 assert v['newFalsePositives']==2 and v['remainingUnclassified']==4361 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['productTestsExecuted']==v['productClassesInitialized']==v['heldFourInitializations']==v['newCompilerExecutions']==v['actualBackendActions']==v['newAcceptance']==0 and all(v[n] is False for n in ['originalProducerOrScannerExecuted','javaMainOrTestExecuted','privateRawOrRuntimeArchiveRead','capturedValuesWritten','captureValueHashesWritten','oldOrCurrentRunQualified','wholeSourceIdentityQualified','wholeG07Accepted','whole451Accepted'])
contract(m);checks=0
for n,val in [('newFalsePositives',3),('remainingUnclassified',0),('actualSecretCount',0),('productClassesInitialized',1),('newCompilerExecutions',1),('heldFourInitializations',1),('javaMainOrTestExecuted',True),('privateRawOrRuntimeArchiveRead',True),('oldOrCurrentRunQualified',True),('wholeSourceIdentityQualified',True),('wholeG07Accepted',True),('whole451Accepted',True)]:
 bad=copy.deepcopy(m);bad[n]=val
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false static provenance acceptance')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),inputFiles=cfg['inputFiles'],originalMetadata=cfg['originalMetadata'],priorUpdateRefs=m['priorUpdateRefs'],updates=dict(path=str((S/'updates.json').relative_to(R)),sha256=sha(S/'updates.json')),newFalsePositives=2,remainingUnclassified=4361,binaryOrContainerLimited=22,actualSecretCount=None,typedMapFiles=typed,candidateRows=1548,independentExistingStaticClassReads=2,retainedStatusCounts=dict(status),metadataNegativeChecks=checks,productTestsExecuted=0,productClassesInitialized=0,newCompilerExecutions=0,heldFourInitializations=0,actualBackendActions=0,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,newFalsePositives=2,remaining=4361,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
