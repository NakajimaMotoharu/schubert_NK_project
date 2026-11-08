"""New capture aliases to pinned already-verified public SDK byte proofs; metadata IO only."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();C=B/'input/743_g07_existing_sdk_alias17_scope.json';cfg=load(C);O=B/'evidence/PG24612-g07-existing-sdk-alias17-provenance-v1';assert not O.exists();keyNames=['path','ruleId','startLine','endLine','inputSha256'];key=lambda v:tuple(v[k] for k in keyNames)
def pinned(ref):
 p=R/ref['path'];assert p.is_relative_to(B) and sha(p)==ref['sha256'];return load(p)
previous=pinned(cfg['previousUpdateManifest']);provider=pinned(cfg['provider']);independent=pinned(cfg['providerIndependent']);proven=pinned(cfg['providerUpdates']);assert independent['producerManifest']==cfg['provider'] and independent['updates']==cfg['providerUpdates'];assert provider['actualExit']==independent['actualExit']==0 and provider['newFalsePositives']==independent['newFalsePositives']==594 and provider['actualDistinctSdkArtifactsRead']==independent['independentlyReadSdkArtifacts']==9 and provider['updatesSha256']==cfg['providerUpdates']['sha256'] and independent['wholeG07Accepted'] is False
refs=[*previous['priorUpdateRefs'],dict(path=str((R/cfg['previousUpdateManifest']['path']).with_name('updates.json').relative_to(R)),sha256=previous['updatesSha256'])];prior=[]
for ref in refs:prior+=pinned(ref)
rows=pinned(cfg['originalMetadata']);original=Counter(map(key,rows));old=Counter(map(key,prior));assert len(rows)==4493 and len(prior)==1196 and sum((original-old).values())==3297
rule=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);cache={};readset={}
def observed(f,role,name):
 path=f['path'];assert path.startswith('evidence/01_PT/018_NK-OPS-001/evidence/') and path.endswith('/manifest.json') and not any(t.lower() in path.lower() for t in cfg['protectedNameTokens'])
 if path not in cache:
  p=R/path;assert sha(p)==f['inputSha256'];cache[path]=(p.read_text(),load(p));readset[path]=sha(p)
 text,obj=cache[path];assert f['ruleId']=='generic-api-key' and f['startLine']==f['endLine'];a=0;z=len(text)
 for depth,part in enumerate(role.split('.'),1):
  positions=[v for v in re.finditer(r'^'+' '*(2*depth)+re.escape(json.dumps(part))+r': ',text,re.M) if a<=v.start()<z];assert len(positions)==1;at=positions[0].end();v,end=json.JSONDecoder().raw_decode(text,at);obj=obj[part];assert obj==v;a,z=at,end
 assert type(obj) is dict and type(obj.get(name)) is str
 lines=text.splitlines(keepends=True);line=lines[f['startLine']-1];start=sum(map(len,lines[:f['startLine']-1]));assert a<=start<z
 pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line);assert pair and json.loads(pair[1])==name and pair[2]==obj[name]
 first=max(0,f['startLine']-2);window=''.join(lines[first:min(len(lines),f['endLine']+1)]);capture={m[1] for m in rx.finditer(window) if f['startLine']<=first+window[:m.start(1)].count('\n')+1<=first+window[:m.end(1)].count('\n')+1<=f['endLine']};assert capture=={pair[2]};return pair[2]
updates=[];providerPaths=set();providerRows=[]
for t in cfg['targets']:
 assert original[key(t)]==1 and not old[key(t)] and t['inputSha256']==cfg['inputFiles'][t['path']] and t['role'] in ['libraryHashes','auxJarSha256']
 reference=t['referenceName'];assert reference.startswith(cfg['guestReferencePrefix']) and t['provenSdkPath']==cfg['provenSdkPrefix']+reference[len(cfg['guestReferencePrefix']):]
 sdk=t['provenSdkPath'];assert sdk in provider['sdkArtifactReadset'];coordinate=provider['sdkArtifactReadset'][sdk]['coordinate'];assert sdk==cfg['provenSdkPrefix']+coordinate['groupId'].replace('.','/')+'/'+coordinate['artifactId']+'/'+coordinate['version']+'/'+coordinate['artifactId']+'-'+coordinate['version']+'.jar'
 value=observed(t,t['role'],reference);candidates=[p for p in proven if p['sdkPath']==sdk and p['actualSdkJarByteHashMatched'] is True and p['wholeExactCapturePubliclyDerived'] is True and p['exactCaptureCount']==1 and p['artifactLoadedOrExecuted'] is False and p['oldOrCurrentRunQualified'] is False];assert candidates
 witness=candidates[0];assert original[key(witness)]==1 and observed(witness,witness['fieldRole'],sdk)==value
 providerPaths.add(sdk);providerRef={k:witness[k] for k in keyNames};providerRows.append(providerRef)
 updates.append(dict(**{k:t[k] for k in keyNames},disposition='FALSE_POSITIVE_CAPTURE_ALIAS_TO_EXISTING_ACTUAL_PUBLIC_SDK_DIGEST_PROOF',fieldRole=t['role'],referenceName=reference,provenSdkPath=sdk,mavenCoordinate=coordinate,providerFinding=providerRef,providerProof=cfg['provider'],providerIndependent=cfg['providerIndependent'],wholeExactCapturePubliclyDerived=True,exactCaptureCount=1,sdkByteProofReused=True,newArtifactIo=False,oldGuestPathIo=False,capturedValueWritten=False,captureValueHashWritten=False,oldOrCurrentRunQualified=False))
new=Counter(map(key,updates));assert len(updates)==17 and len(new)==17 and not new.keys()&old.keys();assert all(original[k]==v==1 for k,v in new.items());remaining=sum((original-old-new).values());assert remaining==3280 and len(providerPaths)==9
O.mkdir();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');write(O/'updates.json',updates);out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),originalMetadata=cfg['originalMetadata'],priorUpdateRefs=refs,provider=cfg['provider'],providerIndependent=cfg['providerIndependent'],providerUpdates=cfg['providerUpdates'],readOnlyPublicMetadataFiles=readset,candidateRows=17,newFalsePositives=17,cumulativeClassified=1213,remainingUnclassified=remaining,actualSecretCount=None,binaryOrContainerLimited=22,providerSdkArtifactsReused=9,sdkArtifactsReRead=0,actualArtifactIo=0,productTestsExecuted=0,productClassesInitialized=0,javaOrMavenExecuted=False,downloadExecuted=False,oldGuestPathIo=False,oldProductJarRead=False,privateRawRead=False,capturedValuesWritten=False,captureValueHashesWritten=False,oldOrCurrentRunQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,updatesSha256=sha(O/'updates.json'),tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,newFalsePositives=17,remaining=remaining,metadataFiles=len(readset),artifactsRead=0,manifestSha256=sha(O/'manifest.json'))))
