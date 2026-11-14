"""Bind the actual v4 full static outputs to unchanged, individually reviewed source sites."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';w=r.parent/'pgpt-runs/PG379/pg30748-haruka-common91-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=b/'evidence/PG30750-haruka-common91-full-static-raw-v4/manifest.json';s=json.loads(sp.read_text());cfg=json.loads((w/'payload-config.json').read_text());old=json.loads((i/'2571_common91_exact_static_admission.json').read_text())
assert s['sourceCommit']==cfg['sourceCommit']=='cf868540e7e461dc1809e4f0b7a677ccddeed168'
assert s['actualExit']==s['compileStatic']['actualExit']==0 and s['compileStatic']['ownedProcessGroupAbsent'] is True
assert not s['processingErrors'] and s['checkstyleErrors']==0 and all(v==0 for v in s['spotbugs'].values())
assert s['standardResourceCopyVerified'] and len(s['resourceOutputs'])==7
for row in s['resourceOutputs']:assert row['sha256']==cfg['payloadHashes']['source/program/characterization/tests/resources/'+row['path']]
assert collections.Counter(x['rule'] for x in s['rawFindings'])==dict(UseConcurrentHashMap=24,CloseResource=6,DoNotUseThreads=29,UseProperClassLoader=1)
prefix='/home/mini/schubert-nk-pgpt/runs/pg30748-common91-v4/payload/source/';remaining=list(old['sourceAnchors']);rows=[]
for raw in s['rawFindings']:
 assert raw['path'].startswith(prefix);name=raw['path'][len(prefix):];p=r/name;line=int(raw['beginline']);anchor=p.read_text().splitlines()[line-1].strip()
 candidates=[x for x in remaining if x['path']==name and x['rule']==raw['rule'] and x['sourceLine']==line and x['message']==raw['message'] and x['method']==raw.get('method') and x['variable']==raw.get('variable')]
 assert len(candidates)==1;row=candidates[0];assert row['sha256']==sha(p)==cfg['payloadHashes']['source/'+name] and row['sourceAnchor']==anchor
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['sourceCommit']+':'+name])).hexdigest()==row['sha256']
 remaining.remove(row);rows.append(row)
assert not remaining and len(rows)==60
ad=dict(old,sourceCommit=cfg['sourceCommit'],prepareSha256=sha(sp),sourceAnchors=rows,priorSiteReview=dict(path=str((i/'2571_common91_exact_static_admission.json').relative_to(r)),sha256=sha(i/'2571_common91_exact_static_admission.json')),actualNewStaticRun=True,standardResourceCopyVerified=True)
p=i/'2577_common91_v4_static_admission.json';p.open('x').write(json.dumps(ad,ensure_ascii=False,indent=2)+'\n')
e=b/'evidence/PG30746-common91-v4-full-static-independent-admission-v1';assert not e.exists();e.mkdir();result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=cfg['sourceCommit'],actualStatic=dict(path=str(sp.relative_to(r)),sha256=sha(sp)),admission=dict(path=str(p.relative_to(r)),sha256=sha(p)),raw=60,individuallyExactByteAndAnchorMatched=60,applicable=0,unclassified=0,checkstyle=0,spotbugs=0,processingErrors=0,actualStandardResources=7,whole91NotYetExecuted=True,formalAccepted=False);(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result))
