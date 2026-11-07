"""Independent whole scalar role/current normal member-byte comparison; no target execution."""
from pathlib import Path
from collections import Counter
from contextlib import ExitStack
import datetime,json,hashlib,re,zipfile,struct,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001/evidence';S=B/'PG23564-g07-main-class-hash47-provenance-v1';O=B/'PG23566-g07-main-class-hash47-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda x:tuple(x[n] for n in ['path','ruleId','startLine','endLine','inputSha256'])
def binary_name(raw):
 assert raw[:4]==bytes.fromhex('cafebabe');version=struct.unpack_from('>H',raw,6)[0];assert version==69;count=struct.unpack_from('>H',raw,8)[0];at=10;strings={};classes={};i=1
 while i<count:
  kind=raw[at];at+=1
  if kind==1:
   size=struct.unpack_from('>H',raw,at)[0];at+=2;strings[i]=raw[at:at+size];at+=size
  elif kind==7:classes[i]=struct.unpack_from('>H',raw,at)[0];at+=2
  elif kind in (8,16,19,20):at+=2
  elif kind in (3,4,9,10,11,12,17,18):at+=4
  elif kind in (5,6):at+=8;i+=1
  elif kind==15:at+=3
  else:raise AssertionError('bad passive class tag')
  i+=1
 this=struct.unpack_from('>H',raw,at+2)[0];return strings[classes[this]].decode('utf-8')
assert not O.exists();m=load(S/'manifest.json');assert sha(S/'manifest.json')=='602af5cdaa97f5904d7f5f999c6cbb2954c9814ec0a0d0b9e32418d424534daa' and m['actualExit']==0;cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256'];normal=Path(m['normalManifest']['path']);assert sha(normal)==m['normalManifest']['sha256']==cfg['normalManifestSha256'];nm=load(normal);assert nm['source']==m['normalCoreSource']==cfg['normalSource'];assert all(sha(Path(v['path']))==v['sha256'] for v in nm['jars'].values())
inputp=R/m['input']['path'];assert sha(inputp)==m['input']['sha256']==cfg['artifactSha256'];text=inputp.read_text();obj=load(inputp);mapping=obj['result']['allPhysicalMainSha256'];assert len(mapping)==1644;origin=R/m['originalMetadata']['path'];assert sha(origin)==m['originalMetadata']['sha256'];rows=load(origin);assert len(rows)==4493;original=Counter(map(key,rows));prior=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==128 and sum((original-old).values())==4365;selected=[v for v in rows if v['path']==cfg['artifactPath'] and not old[key(v)]];assert len(selected)==47;rule=B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)==m['ruleManifestSha256'];rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);lines=text.splitlines(keepends=True)
# Independent indentation/type-role association; only this dictionary has six-space scalar keys.
start=next(i for i,v in enumerate(lines,1) if v=='    "allPhysicalMainSha256": {\n');stop=next(i for i,v in enumerate(lines[start:],start+1) if v=='    },\n');expected=[];kept=[];reads=0;statuscounts=Counter()
with ExitStack() as stack:
 jars={n:stack.enter_context(zipfile.ZipFile(v['path'])) for n,v in nm['jars'].items()};members={n:set(j.namelist()) for n,j in jars.items()}
 for f in selected:
  base={k:f[k] for k in ['path','ruleId','startLine','endLine','inputSha256']};line=''.join(lines[f['startLine']-1:f['endLine']]);match=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line)
  if not f['startLine']==f['endLine'] or not start<f['startLine']<stop or match is None:kept.append(dict(**base,status='UNKNOWN_NONSCALAR_OR_OUTSIDE_TYPED_MAP'));continue
  token=json.loads(match[1]);value=match[2];assert mapping.get(token)==value;lo=max(0,f['startLine']-2);window=''.join(lines[lo:min(len(lines),f['endLine']+1)]);cap=set()
  for a in rx.finditer(window):
   first=lo+window[:a.start(1)].count('\n')+1;last=lo+window[:a.end(1)].count('\n')+1
   if f['startLine']<=first<=last<=f['endLine']:cap.add(a[1])
  assert cap=={value}
  if any(v.lower() in token.lower() for v in cfg['protectedNameTokens']):kept.append(dict(**base,status='PROTECTED_NAME_NO_MEMBER_IO'));continue
  parts=token.split(':',1)
  if len(parts)!=2 or parts[0] not in jars or not re.fullmatch(r'dev/codex/schubert/nk/[A-Za-z0-9_$/]+\.class',parts[1]) or '..' in token:kept.append(dict(**base,status='UNKNOWN_MAIN_MEMBER_KEY'));continue
  module,member=parts
  if member not in members[module]:kept.append(dict(**base,status='CURRENT_NORMAL_CLASS_UNAVAILABLE'));continue
  raw=jars[module].read(member);reads+=1;assert binary_name(raw)==member[:-6]
  if hashlib.sha256(raw).hexdigest()!=value:kept.append(dict(**base,status='CURRENT_NORMAL_MODULE_OR_BYTE_SHA_MISMATCH'));continue
  expected.append(dict(**base,disposition='FALSE_POSITIVE_ACTUAL_PUBLIC_NORMAL_MAIN_CLASS_DIGEST',fieldRole='result.allPhysicalMainSha256',exactCaptureCount=1,wholeExactCapturePubliclyDerived=True,normalModule=module,classEntry=member,internalBinaryName=member[:-6],normalCompileManifestSha256=sha(normal),normalJarSha256=nm['jars'][module]['sha256'],actualClassMemberHashMatched=True,guardedClassMetadataOnly=any(x in member for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']),oldOrCurrentRunQualified=False,capturedValueWritten=False,captureValueHashWritten=False))
updates=load(S/'updates.json');retained=load(S/'retained.json');assert sha(S/'updates.json')==m['updatesSha256'] and sha(S/'retained.json')==m['retainedSha256'];assert updates==expected==[] and retained==kept and len(kept)==47;assert Counter(map(key,kept))==Counter(map(key,selected));assert m['newFalsePositives']==0 and m['remainingUnclassified']==4365
for v in kept:statuscounts[v['status']]+=1
# Mismatched/absent bytes remain unknown, never a class-loader or old-run fallback.
def contract(v):
 assert v['newFalsePositives']==0 and v['remainingUnclassified']==4365 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['productTestsExecuted']==v['productClassesInitialized']==v['heldFourInitializations']==v['actualAuthOrDbActions']==v['newAcceptance']==0 and all(v[k] is False for k in ['scannerExecuted','oldProducerExecuted','targetsExecuted','privateRawRead','runtimeArchiveRead','jarMembersExtractedToFilesystem','capturedValuesWritten','captureValueHashesWritten','oldOrCurrentRunQualified','wholeG07Accepted','whole451Accepted'])
contract(m);checks=0
for k,val in [('newFalsePositives',1),('remainingUnclassified',4364),('actualSecretCount',0),('productClassesInitialized',1),('heldFourInitializations',1),('runtimeArchiveRead',True),('oldOrCurrentRunQualified',True),('wholeG07Accepted',True)]:
 bad=copy.deepcopy(m);bad[k]=val
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('unknown normalized to acceptance')
assert sha(R/m['tool']['path'])==m['tool']['sha256'];O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str((S/'manifest.json').relative_to(R)),sha256=sha(S/'manifest.json')),normalCoreSource=nm['source'],normalManifest=m['normalManifest'],candidateRows=47,independentlyReadNormalClassMembers=reads,retainedStatusCounts=dict(statuscounts),newFalsePositives=0,remainingUnclassified=4365,actualSecretCount=None,binaryOrContainerLimited=22,metadataNegativeChecks=checks,productTestsExecuted=0,productClassesInitialized=0,heldFourInitializations=0,actualAuthOrDbActions=0,scannerExecuted=False,oldProducerExecuted=False,targetsExecuted=False,privateRawRead=False,runtimeArchiveRead=False,jarMembersExtractedToFilesystem=False,capturedValuesWritten=False,captureValueHashesWritten=False,oldOrCurrentRunQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,classified=0,retained=47,remaining=4365,classMembersRead=reads,statuses=dict(statuscounts),manifestSha256=sha(O/'manifest.json'))))
