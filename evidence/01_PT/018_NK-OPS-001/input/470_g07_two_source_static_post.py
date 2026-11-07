"""Independently verify two whole-source static compiler artifacts; no target execution."""
from pathlib import Path
from collections import Counter
import json,hashlib,subprocess,datetime,re,struct,zipfile,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG23578-g07-two-source-static-independent-v1';S=R.parent/'pgpt-runs/PG379/pg23576-g07-two-source-static-compile-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda x:tuple(x[n] for n in ['path','ruleId','startLine','endLine','inputSha256'])
def name_of(raw):
 assert raw[:4]==bytes.fromhex('cafebabe') and struct.unpack_from('>H',raw,6)[0]==69
 n=struct.unpack_from('>H',raw,8)[0];a=10;i=1;utf={};classes={}
 while i<n:
  tag=raw[a];a+=1
  if tag==1:size=struct.unpack_from('>H',raw,a)[0];a+=2;utf[i]=raw[a:a+size];a+=size
  elif tag==7:classes[i]=struct.unpack_from('>H',raw,a)[0];a+=2
  elif tag in (8,16,19,20):a+=2
  elif tag in (3,4,9,10,11,12,17,18):a+=4
  elif tag in (5,6):a+=8;i+=1
  elif tag==15:a+=3
  else:raise AssertionError('invalid class metadata')
  i+=1
 return utf[classes[struct.unpack_from('>H',raw,a+2)[0]]].decode()
assert not O.exists();pfp=B/'evidence/PG23574-g07-two-source-static-preflight-v1/manifest.json';assert sha(pfp)=='f619be3f31a787b6849499ad30a208cba2d304ac23b65236ddbd9a78ecd5d395';pf=load(pfp);mp=S/'manifest.json';assert sha(mp)=='493dc56dd01f971a43d763a1fe699a38eb831d8d1dc539fcb79a9c49281708a7';m=load(mp);begin=load(S/'begin.json');assert begin==m['begin'];assert m['stage']==load(S/'javac-exit.safe.json');stage=m['stage'];assert stage['actualExit']==0 and stage['timedOut'] is False and stage['startUTC']>=begin['startUTC'];assert sha(S/'javac.stdout')==stage['stdoutSha256'] and sha(S/'javac.stderr')==stage['stderrSha256'];assert sha(R/begin['tool']['path'])==begin['tool']['sha256'];assert begin['sourceSha256']==pf['sourceSha256'] and begin['dependencies']==pf['dependencies'];assert pf['compilerFlags']==['-proc:none','-implicit:none','--release','25','-encoding','UTF-8','-g','-Xlint:all','-Werror']
paths=pf['sourcePaths'];assert len(paths)==2 and set(pf['sourceBlobIds'])==set(paths);assert sorted(str(v.relative_to(S/'snapshot')) for v in (S/'snapshot').rglob('*.java'))==sorted(paths)
for n in paths:
 assert '/src/main/java/' in n and n.endswith(('MediaApplicationService.java','ScenarioApplicationService.java'))
 oid=subprocess.check_output(['git','rev-parse',pf['historicalPublicSource']+':'+n],cwd=R,text=True).strip();assert oid==pf['sourceBlobIds'][n];raw=subprocess.check_output(['git','cat-file','blob',oid],cwd=R);assert raw==(S/'snapshot'/n).read_bytes() and hashlib.sha256(raw).hexdigest()==pf['sourceSha256'][n]
 current=subprocess.check_output(['git','show',pf['currentNormalCoreSource']+':'+n],cwd=R);assert (R/n).read_bytes()==current
for n,h in pf['dependencies'].items():
 p=Path(n);assert sha(p)==h
 with zipfile.ZipFile(p) as z:assert not any(x in z.namelist() for x in ['META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin'])
assert sha(R.parent/'toolchain/jdk-25.0.4/release')==pf['jdkReleaseSha256'];cmd=[str(R.parent/'toolchain/jdk-25.0.4/bin/javac'),'-J-Djava.io.tmpdir='+str(S/'tmp'),'-J-Xlog:class+init=info:file='+str(S/'compiler-class-init.log'),*pf['compilerFlags'],'-sourcepath',str(S/'snapshot/src/schubert-nk-api/src/main/java'),'-classpath',':'.join(pf['dependencies']),'-d',str(S/'classes'),*[str(S/'snapshot'/n) for n in paths]];assert cmd==begin['command']==stage['command'];init=(S/'compiler-class-init.log').read_text();assert init and not re.search(r"Initializing '(?:dev/|dev\.)codex[/\.]schubert[/\.]nk[/\.]",init);assert m['productClassesInitialized']==[]
agg=hashlib.sha256();inventory=[]
for p in sorted((S/'classes').rglob('*.class')):
 raw=p.read_bytes();entry=str(p.relative_to(S/'classes'));assert name_of(raw)==entry[:-6];label=entry.encode();agg.update(len(label).to_bytes(8,'big'));agg.update(label);agg.update(len(raw).to_bytes(8,'big'));agg.update(raw);inventory.append(dict(classEntry=entry,bytes=len(raw)))
assert inventory==m['compilerOutputInventory'] and len(inventory)==24 and agg.hexdigest()==m['wholeCompilerOutputAggregateSha256'];assert all(v['classEntry'].startswith(('dev/codex/schubert/nk/api/application/media/MediaApplicationService','dev/codex/schubert/nk/api/application/scenario/ScenarioApplicationService')) for v in inventory)
refm=B/'evidence/PG23564-g07-main-class-hash47-provenance-v1/manifest.json';assert sha(refm)=='602af5cdaa97f5904d7f5f999c6cbb2954c9814ec0a0d0b9e32418d424534daa';old=load(refm);ap=R/old['input']['path'];assert sha(ap)==old['input']['sha256'];text=ap.read_text();data=load(ap);assert data['result']['productionSource']==pf['historicalPublicSource'];mapping=data['result']['allPhysicalMainSha256'];lines=text.splitlines(keepends=True);lo=next(i for i,s in enumerate(lines,1) if s=='    "allPhysicalMainSha256": {\n');hi=next(i for i,s in enumerate(lines[lo:],lo+1) if s=='    },\n');rp=B/'evidence/provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rp)==old['ruleManifestSha256'];rx=re.compile(load(rp)['rules']['generic-api-key']['regex'],re.ASCII);origin=R/old['originalMetadata']['path'];assert sha(origin)==old['originalMetadata']['sha256'];rows=load(origin);assert len(rows)==4493;original=Counter(map(key,rows));prior=[]
for ref in old['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
previous=Counter(map(key,prior));assert len(prior)==128 and all(v==1 for v in previous.values());assert sum((original-previous).values())==4365;targetkeys={'api:'+n for n in pf['targetClassEntries']};updates=[];comparisons=[]
for entry in pf['targetClassEntries']:
 p=S/'classes'/entry;assert name_of(p.read_bytes())==entry[:-6];match=sha(p)==mapping['api:'+entry];comparisons.append(dict(classEntry=entry,exists=True,matchesRecordedCapture=match))
for f in rows:
 if f['path']!=str(ap.relative_to(R)) or previous[key(f)] or f['startLine']!=f['endLine'] or not lo<f['startLine']<hi:continue
 line=lines[f['startLine']-1];a=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line)
 if a is None or json.loads(a[1]) not in targetkeys:continue
 token=json.loads(a[1]);expected=a[2];assert mapping[token]==expected and f['inputSha256']==sha(ap);base=max(0,f['startLine']-2);window=''.join(lines[base:min(len(lines),f['endLine']+1)]);captures={v[1] for v in rx.finditer(window) if f['startLine']<=base+window[:v.start(1)].count('\n')+1<=base+window[:v.end(1)].count('\n')+1<=f['endLine']};assert captures=={expected}
 if sha(S/'classes'/token.split(':',1)[1])!=expected:continue
 updates.append(dict(**{n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']},disposition='FALSE_POSITIVE_STATIC_WHOLE_PUBLIC_SOURCE_CLASS_DIGEST',fieldRole='result.allPhysicalMainSha256',classEntry=token.split(':',1)[1],historicalPublicSource=pf['historicalPublicSource'],sourceBlobIds=pf['sourceBlobIds'],sourceSha256=pf['sourceSha256'],staticCompilerManifestSha256=sha(mp),wholeExactCapturePubliclyDerived=True,actualStaticClassMemberHashMatched=True,oldOrCurrentRunQualified=False,capturedValueWritten=False,captureValueHashWritten=False))
assert comparisons==m['targetComparisons'] and len(updates)==2 and all(v['matchesRecordedCapture'] for v in comparisons);new=Counter(map(key,updates));assert not previous.keys()&new.keys() and all(v==original[k]==1 for k,v in new.items());remaining=sum((original-previous-new).values());assert remaining==4363
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),staticCompilerManifest=dict(path=str(mp),sha256=sha(mp)),preflight=dict(path=str(pfp.relative_to(R)),sha256=sha(pfp)),originalMetadata=old['originalMetadata'],priorUpdateRefs=old['priorUpdateRefs'],input=old['input'],sourceSha256=pf['sourceSha256'],historicalPublicSource=pf['historicalPublicSource'],currentNormalCoreSource=pf['currentNormalCoreSource'],fullUnmodifiedSourceFiles=2,compilerGeneratedClasses=24,staticTargetByteMatches=2,targetComparisons=comparisons,compilerOutputAggregateSha256=agg.hexdigest(),newFalsePositives=2,remainingUnclassified=remaining,binaryOrContainerLimited=22,actualSecretCount=None,productTestsExecuted=0,productClassesInitialized=0,heldFourSourcesCompiled=0,javaMainOrTestExecuted=False,annotationProcessorOrPluginExecuted=False,actualRootOrNativeOperations=0,currentProductionSourceModified=False,oldOrCurrentRunQualified=False,originalBuildSuccessQualified=False,wholeG07Accepted=False,whole451Accepted=False,capturedValuesWritten=False,captureValueHashesWritten=False,newAcceptance=0,formalUpdated=False,effortRate=None)
def contract(v):
 assert v['newFalsePositives']==v['staticTargetByteMatches']==2 and v['remainingUnclassified']==4363 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['fullUnmodifiedSourceFiles']==2 and v['productTestsExecuted']==v['productClassesInitialized']==v['heldFourSourcesCompiled']==v['actualRootOrNativeOperations']==v['newAcceptance']==0 and all(v[n] is False for n in ['javaMainOrTestExecuted','annotationProcessorOrPluginExecuted','currentProductionSourceModified','oldOrCurrentRunQualified','originalBuildSuccessQualified','wholeG07Accepted','whole451Accepted','capturedValuesWritten','captureValueHashesWritten'])
contract(out);checks=0
for n,v in [('staticTargetByteMatches',1),('remainingUnclassified',0),('actualSecretCount',0),('fullUnmodifiedSourceFiles',1),('productClassesInitialized',1),('heldFourSourcesCompiled',1),('javaMainOrTestExecuted',True),('annotationProcessorOrPluginExecuted',True),('oldOrCurrentRunQualified',True),('originalBuildSuccessQualified',True),('wholeG07Accepted',True),('whole451Accepted',True)]:
 bad=copy.deepcopy(out);bad[n]=v
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid static-artifact acceptance')
O.mkdir();write(O/'updates.json',updates);out.update(updatesSha256=sha(O/'updates.json'),metadataNegativeChecks=checks,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,newFalsePositives=2,remainingUnclassified=remaining,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
