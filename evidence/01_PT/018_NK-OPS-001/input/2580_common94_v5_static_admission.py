"""Bind the actual v4 full static outputs to unchanged, individually reviewed source sites."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';w=r.parent/'pgpt-runs/PG379/pg30764-haruka-common94-v5';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=b/'evidence/PG30766-haruka-common94-full-static-raw-v5/manifest.json';s=json.loads(sp.read_text());cfg=json.loads((w/'payload-config.json').read_text());old=json.loads((i/'2571_common91_exact_static_admission.json').read_text())
assert s['sourceCommit']==cfg['sourceCommit']=='95d737c0185c09422290b61b6e61621816b44278'
assert s['actualExit']==s['compileStatic']['actualExit']==0 and s['compileStatic']['ownedProcessGroupAbsent'] is True
assert not s['processingErrors'] and s['checkstyleErrors']==0 and all(v==0 for v in s['spotbugs'].values())
assert s['standardResourceCopyVerified'] and len(s['resourceOutputs'])==7
for row in s['resourceOutputs']:assert row['sha256']==cfg['payloadHashes']['source/program/characterization/tests/resources/'+row['path']]
assert collections.Counter(x['rule'] for x in s['rawFindings'])==dict(UseConcurrentHashMap=24,CloseResource=6,DoNotUseThreads=29,UseProperClassLoader=1)
prefix='/home/mini/schubert-nk-pgpt/runs/pg30764-common94-v5/payload/source/';remaining=list(old['sourceAnchors']);rows=[]
for raw in s['rawFindings']:
 assert raw['path'].startswith(prefix);name=raw['path'][len(prefix):];p=r/name;line=int(raw['beginline']);anchor=p.read_text().splitlines()[line-1].strip()
 prior_text=subprocess.check_output(['git','show','f9f9d28f23833257be991d142e105ec4533f7be8:'+name],text=True)
 line_delta=len(p.read_text().splitlines())-len(prior_text.splitlines())
 insertion_line=prior_text[:prior_text.index('  @Test\n')].count('\n')+1 if line_delta else 0
 candidates=[x for x in remaining if x['path']==name and x['rule']==raw['rule'] and x['message']==raw['message'] and x['method']==raw.get('method') and x['variable']==raw.get('variable') and x['sourceLine']+(line_delta if x['sourceLine']>=insertion_line else 0)==line]
 assert len(candidates)==1;row=candidates[0];assert sha(p)==cfg['payloadHashes']['source/'+name] and row['sourceAnchor']==anchor
 prior_hash=row['sha256'];new_hash=sha(p)
 if prior_hash!=new_hash:
  proof=json.loads((b/'evidence/PG30758-common94-independent-boundary-source-v1/manifest.json').read_text())
  hit=[x for x in proof['proof'] if x['path']==name];assert len(hit)==1 and hit[0]['beforeSha256']==prior_hash and hit[0]['afterSha256']==new_hash and hit[0]['allOldTestsByteInverse']
 remaining.remove(row);row=dict(row,sha256=new_hash,sourceLine=line)
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['sourceCommit']+':'+name])).hexdigest()==row['sha256']
 rows.append(row)
assert not remaining and len(rows)==60
ad=dict(old,expectedTests=94,sourceCommit=cfg['sourceCommit'],prepareSha256=sha(sp),sourceAnchors=rows,priorSiteReview=dict(path=str((i/'2571_common91_exact_static_admission.json').relative_to(r)),sha256=sha(i/'2571_common91_exact_static_admission.json')),actualNewStaticRun=True,standardResourceCopyVerified=True)
p=i/'2580_common94_v5_static_admission.json';p.open('x').write(json.dumps(ad,ensure_ascii=False,indent=2)+'\n')
e=b/'evidence/PG30765-common94-v5-full-static-independent-admission-v1';assert not e.exists();e.mkdir();result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=cfg['sourceCommit'],actualStatic=dict(path=str(sp.relative_to(r)),sha256=sha(sp)),admission=dict(path=str(p.relative_to(r)),sha256=sha(p)),raw=60,individuallyExactByteAndAnchorMatched=60,applicable=0,unclassified=0,checkstyle=0,spotbugs=0,processingErrors=0,actualStandardResources=7,whole94NotYetExecuted=True,formalAccepted=False);(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result))
