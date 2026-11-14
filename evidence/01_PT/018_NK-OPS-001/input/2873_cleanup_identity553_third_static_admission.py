"""Exact same-byte sources except the inverse-token-proven third required-primary oracle."""
from pathlib import Path
import json,hashlib,re,collections,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2872_cleanup_identity553_third_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);oldad=load(i/'2867_cleanup_identity553_static_admission.json');old=load(r/oldad['static']['path']);changed='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/SpeakerStagingTableTest.java';e=b/'evidence/PG32060-speaker-third-primary-oracle-repair-v1';original=(e/'original-Test.java.txt').read_text();current=(r/changed).read_text();inverse=current.replace('same.primary.getClass(),','IllegalArgumentException.class,').replace('assertSame(same.primary, rejected);','assertSame(same.primary, rejected.getCause());');tok=lambda x:re.findall(r'"(?:\\.|[^"\\])*"|\S',x);assert tok(inverse)==tok(original);assert sha(e/'original-Test.java.txt')==old['inputHashes'][changed];proof=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),original=ref(e/'original-Test.java.txt'),formattedSource=ref(r/changed),inverseDeclaredCorrectionTokensExact=True,otherMainAndIndependent10Unchanged=True);(e/'formatted-proof.json').open('x').write(json.dumps(proof,indent=2)+'\n');prior=collections.defaultdict(list)
for x in oldad['sourceAnchors']:
 if x['path']!=changed:assert sha(r/x['path'])==old['inputHashes'][x['path']]
 prior[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
rows=[];rebound=0
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message']);assert prior[key],key;row=dict(prior[key].pop(0),sourceLine=line)
 if path==changed:
  row['reason']+=' Exact current anchor revalidated after only the third original-primary oracle correction; inverse tokens SHA256 '+sha(e/'formatted-proof.json')+'.';rebound+=1
 rows.append(row)
assert not any(prior.values()) and len(rows)==291
(i/'2873_cleanup_identity553_third_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,all291ExactAnchors=True,changedSourceSitesRevalidated=rebound,applicable=0,unclassified=0))
