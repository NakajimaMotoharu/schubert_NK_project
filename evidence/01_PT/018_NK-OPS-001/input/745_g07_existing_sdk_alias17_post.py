"""Reverse-join existing SDK witness rows to17 new captures; no binary IO or replay."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime,copy
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();S=B/'evidence/PG24612-g07-existing-sdk-alias17-provenance-v1';O=B/'evidence/PG24614-g07-existing-sdk-alias17-independent-v1';assert not O.exists();mp=S/'manifest.json';assert sha(mp)=='663477323470e5acb1e70b102fc30027679c7a34355268d3a2a5227c14c889c9';m=load(mp);cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp);names=['path','ruleId','startLine','endLine','inputSha256'];key=lambda v:tuple(v[k] for k in names)
for ref in [cfg['provider'],cfg['providerIndependent'],cfg['providerUpdates'],cfg['originalMetadata'],*m['priorUpdateRefs']]:assert sha(R/ref['path'])==ref['sha256']
provider=load(R/cfg['provider']['path']);post=load(R/cfg['providerIndependent']['path']);original=load(R/cfg['originalMetadata']['path']);proven=load(R/cfg['providerUpdates']['path']);assert post['producerManifest']==cfg['provider'] and post['updates']==cfg['providerUpdates'] and provider['updatesSha256']==cfg['providerUpdates']['sha256'] and post['actualExit']==provider['actualExit']==0 and post['newFalsePositives']==provider['newFalsePositives']==594 and post['independentlyReadSdkArtifacts']==9 and post['wholeG07Accepted'] is False
prior=[]
for ref in m['priorUpdateRefs']:prior+=load(R/ref['path'])
old=Counter(map(key,prior));orig=Counter(map(key,original));assert len(original)==4493 and len(prior)==1196 and sum((orig-old).values())==3297
assert sha(S/'updates.json')==m['updatesSha256'];updates=load(S/'updates.json');assert len(updates)==17;bykey={key(v):v for v in updates};assert len(bykey)==17;scope={key(v):v for v in cfg['targets']};assert set(bykey)==set(scope) and not set(scope)&set(old)
rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);readset={};cache={}
def capture(f,role,name):
 path=f['path'];assert path.startswith('evidence/01_PT/018_NK-OPS-001/evidence/') and path.endswith('/manifest.json') and not any(n.lower() in path.lower() for n in cfg['protectedNameTokens'])
 if path not in cache:
  p=R/path;assert sha(p)==f['inputSha256'];cache[path]=(load(p),p.read_text().splitlines(keepends=True));readset[path]=sha(p)
 obj,lines=cache[path];parts=role.split('.');low=0;high=len(lines)+1
 for depth,part in enumerate(parts,1):
  indent=' '*(2*depth);starts=[i for i,line in enumerate(lines,1) if low<i<high and line==indent+json.dumps(part)+': {\n'];assert len(starts)==1;low=starts[0];high=next(i for i,line in enumerate(lines[low:],low+1) if line in [indent+'},\n',indent+'}\n']);obj=obj[part]
 assert f['ruleId']=='generic-api-key' and low<f['startLine']==f['endLine']<high
 line=lines[f['startLine']-1];pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line);assert pair and json.loads(pair[1])==name and obj[name]==pair[2]
 start=max(0,f['startLine']-2);window=''.join(lines[start:min(len(lines),f['endLine']+1)]);matches=[]
 for hit in rx.finditer(window):
  a=start+window[:hit.start(1)].count('\n')+1;z=start+window[:hit.end(1)].count('\n')+1
  if f['startLine']<=a<=z<=f['endLine']:matches.append(hit[1])
 assert set(matches)=={pair[2]};return pair[2]
provenBy={key(v):v for v in proven};used=set()
# Reverse order is independent of producer choice/order; each saved witness must be direct and exact.
for k in sorted(bykey,reverse=True):
 row=bykey[k];t=scope[k];assert orig[k]==1 and row['providerProof']==cfg['provider'] and row['providerIndependent']==cfg['providerIndependent'] and row['fieldRole']==t['role'] and row['referenceName']==t['referenceName'] and row['provenSdkPath']==t['provenSdkPath'];providerKey=key(row['providerFinding']);w=provenBy[providerKey];assert orig[providerKey]==1 and w['actualSdkJarByteHashMatched'] is True and w['wholeExactCapturePubliclyDerived'] is True and w['exactCaptureCount']==1 and w['artifactLoadedOrExecuted'] is False
 sdk=row['provenSdkPath'];assert sdk==w['sdkPath'] and row['mavenCoordinate']==w['mavenCoordinate']==provider['sdkArtifactReadset'][sdk]['coordinate'];coordinate=w['mavenCoordinate'];suffix=coordinate['groupId'].replace('.','/')+'/'+coordinate['artifactId']+'/'+coordinate['version']+'/'+coordinate['artifactId']+'-'+coordinate['version']+'.jar';assert sdk==cfg['provenSdkPrefix']+suffix and row['referenceName']==cfg['guestReferencePrefix']+suffix
 assert capture(t,t['role'],t['referenceName'])==capture(w,w['fieldRole'],sdk);used.add(sdk)
 assert row['sdkByteProofReused'] is True and row['newArtifactIo'] is False and row['oldGuestPathIo'] is False and row['capturedValueWritten'] is False and row['captureValueHashWritten'] is False and row['oldOrCurrentRunQualified'] is False
assert len(used)==9 and readset==m['readOnlyPublicMetadataFiles'];new=Counter(map(key,updates));assert sum((orig-old-new).values())==3280 and all(orig[k]==v==1 for k,v in new.items())
intFields={'actualExit':0,'candidateRows':17,'newFalsePositives':17,'cumulativeClassified':1213,'remainingUnclassified':3280,'binaryOrContainerLimited':22,'providerSdkArtifactsReused':9,'sdkArtifactsReRead':0,'actualArtifactIo':0,'productTestsExecuted':0,'productClassesInitialized':0,'newAcceptance':0};falseFields=['javaOrMavenExecuted','downloadExecuted','oldGuestPathIo','oldProductJarRead','privateRawRead','capturedValuesWritten','captureValueHashesWritten','oldOrCurrentRunQualified','wholeG07Accepted','whole451Accepted','formalUpdated']
def contract(v):
 assert all(type(v[k]) is int and v[k]==n for k,n in intFields.items()) and all(v[k] is False for k in falseFields) and v['actualSecretCount'] is None and v['effortRate'] is None
contract(m);checks=0
for field,value in [('newFalsePositives',18),('remainingUnclassified',3281),('actualSecretCount',0),('sdkArtifactsReRead',1),('actualArtifactIo',1),('privateRawRead',True),('oldGuestPathIo',True),('newAcceptance',1),('oldOrCurrentRunQualified',True),('wholeG07Accepted',True),('whole451Accepted',True),('productTestsExecuted',1),('productClassesInitialized',1),('javaOrMavenExecuted',True),('downloadExecuted',True),('actualArtifactIo',False),('actualExit',False)]:
 bad=copy.deepcopy(m);bad[field]=value;assert json.dumps(bad,sort_keys=True)!=json.dumps(m,sort_keys=True)
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false alias credit')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=m['priorUpdateRefs'],updates=dict(path=str((S/'updates.json').relative_to(R)),sha256=sha(S/'updates.json')),provider=cfg['provider'],providerIndependent=cfg['providerIndependent'],readOnlyPublicMetadataFiles=readset,candidateRows=17,newFalsePositives=17,cumulativeClassified=1213,remainingUnclassified=3280,actualSecretCount=None,binaryOrContainerLimited=22,providerSdkArtifactsReused=9,sdkArtifactsReRead=0,actualArtifactIo=0,metadataNegativeChecks=checks,productTestsExecuted=0,productClassesInitialized=0,oldGuestPathIo=False,oldProductJarRead=False,privateRawRead=False,oldOrCurrentRunQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newFalsePositives=17,remaining=3280,metadataNegatives=checks,artifactIo=0,manifestSha256=sha(O/'manifest.json'))))
