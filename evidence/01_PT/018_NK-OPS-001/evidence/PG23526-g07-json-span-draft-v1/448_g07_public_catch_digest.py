"""Finite G07 public metadata/hash proof; exact source whitelist precedes all source IO."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime,subprocess
from public_java_digest_provenance import digests,captures
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001/evidence';O=B/'PG23518-g07-public-catch-digest-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());key=lambda x:tuple(x[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
ALLOW={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OwnedOutboxDispatcher.java','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogReplayWorker.java'}
def source_allowed(n):
 return n in ALLOW and not any(s in n.lower() for s in ['root','native','auth','access','private','cohort','permit','snapshotkeyclosewitness','pg9892_snapshot','rootfailedstart','/security/','/session/'])
assert all(source_allowed(n) for n in ALLOW)
assert not O.exists();origin=B/'provisional/PG9888-g07-capture-shape-v1';om=load(origin/'manifest.json');assert sha(origin/'residual-metadata-shapes.json')==om['residualMetadataSha256']=='a3de442acaed6f826bd6428eec3885a58b07e5a4f0a16f9b1b06b2318ffefd72';rows=load(origin/'residual-metadata-shapes.json');assert len(rows)==4493;original=Counter(map(key,rows));done=[];refs=[]
for n in ['PG22160-g07-three-public-test-symbols-v1','PG22170-g07-four-selector-symbols-v1','PG22184-g07-two-public-class-references-v2','PG22328-g07-two-typed-class-symbols-v1']:
 p=B/n/'manifest.json';m=load(p);u=p.with_name('updates.json');assert sha(u)==m['updatesSha256'];done.extend(load(u));refs.append(dict(path=str(u.relative_to(R)),sha256=sha(u)))
donecounter=Counter(map(key,done));assert len(done)==11 and sum((original-donecounter).values())==4482
name='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG6542-jdbc-catch-inventory-v1/sites.json';p=R/name;selected=[x for x in rows if x['path']==name and not donecounter[key(x)]];assert len(selected)==73 and len({x['inputSha256'] for x in selected})==1;assert sha(p)==selected[0]['inputSha256'];text=p.read_text();sites=load(p);assert len(sites)==113 and text==json.dumps(sites,sort_keys=True,ensure_ascii=False,indent=2)+'\n';im=load(p.with_name('manifest.json'));assert sha(p)==im['inventorySha256'] and im['source']=='1b663c1b0271c3e9318701a16e12b378e1ffaa5d'
rule=B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII)
# JSON object spans preserve the exact original capture-to-property binding, no line heuristic.
decoder=json.JSONDecoder();at=1;objects=[]
while True:
 while text[at].isspace() or text[at]==',':at+=1
 if text[at]==']':break
 value,length=decoder.raw_decode(text,at);objects.append((value,at,at+length));at+=length
assert [x[0] for x in objects]==sites
normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);pins={};derivations={}
for n in sorted(ALLOW):
 assert source_allowed(n);src=R/n;assert not src.is_symlink() and src.resolve()==src;h=sha(src);assert nm['begin']['inputHashes'][n]==h;pins[n]=h;derivations[n]={x['catchLine']:x['publicTokenDigest'] for x in digests(src.read_text())}
updates=[];retained=[];lines=text.splitlines(keepends=True)
for finding in selected:
 lo=sum(map(len,lines[:finding['startLine']-1]));hi=sum(map(len,lines[:finding['endLine']]));objs=[(v,a,z) for v,a,z in objects if a<=lo and hi<=z+1];assert len(objs)==1;v,a,z=objs[0];n=v['sourcePath']
 if not source_allowed(n):retained.append(dict(**{k:finding[k] for k in ['path','ruleId','startLine','endLine','inputSha256']},status='SOURCE_NOT_IN_EXACT_ALLOWED_READ_SET'));continue
 if pins[n]!=v['sourceSha256']:retained.append(dict(**{k:finding[k] for k in ['path','ruleId','startLine','endLine','inputSha256']},status='CURRENT_SOURCE_CHANGED'));continue
 got=captures(lines,finding,rx);rawline=''.join(lines[finding['startLine']-1:finding['endLine']]);token=re.fullmatch(r'\s+"bodyTokenSha256": "([a-f0-9]{64})",?\n?',rawline);assert token and got=={token[1]}=={v['bodyTokenSha256']} and len(got)==1
 if derivations[n].get(v['beginLine'])!=v['bodyTokenSha256']:retained.append(dict(**{k:finding[k] for k in ['path','ruleId','startLine','endLine','inputSha256']},status='BODY_TOKEN_DERIVATION_UNPROVEN'));continue
 updates.append(dict(**{k:finding[k] for k in ['path','ruleId','startLine','endLine','inputSha256']},disposition='FALSE_POSITIVE_PUBLIC_SOURCE_SQLCATCH_DIGEST',sourcePath=n,sourceSha256=pins[n],catchLine=v['beginLine'],fieldRole='bodyTokenSha256',wholeExactCapturePubliclyDerived=True,capturedValueWritten=False,captureValueHashWritten=False,productBehaviorQualified=False))
new=Counter(map(key,updates));assert len(updates)==sum(new.values()) and not new.keys()&donecounter.keys() and all(v==1 and original[k]==1 for k,v in new.items());remaining=sum((original-donecounter-new).values());assert remaining==4482-len(updates)
O.mkdir();write(O/'updates.json',updates);write(O/'retained.json',retained);out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerHeadAtExecution=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),normalCoreSource=nm['source'],historicalScanSource='fb9fce0f91de3d9fdfa634fe277592700f915e45',historicalMetadataFindings=4493,previousUpdates=11,originalMetadataSha256=sha(origin/'residual-metadata-shapes.json'),input=dict(path=name,sha256=sha(p)),originalInventoryManifestSha256=sha(p.with_name('manifest.json')),priorUpdateRefs=refs,ruleManifestSha256=sha(rule),allowedSources=sorted(ALLOW),sourcePins=pins,candidateRows=73,newFalsePositives=len(updates),remainingUnclassified=remaining,retainedRows=len(retained),updatesSha256=sha(O/'updates.json'),retainedSha256=sha(O/'retained.json'),sourceReadSetExpandedBeyondWhitelist=False,actualSecretCount=None,binaryOrContainerLimited=22,productTestsExecuted=0,scannerExecuted=False,targetsExecuted=False,privateRawRead=False,actualBackendActions=0,capturedValuesWritten=False,captureValueHashesWritten=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,classified=len(updates),retained=len(retained),remaining=remaining,manifestSha256=sha(O/'manifest.json'))))
