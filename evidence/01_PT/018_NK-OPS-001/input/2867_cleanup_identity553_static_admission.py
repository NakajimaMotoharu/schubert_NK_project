"""Revalidate every old exact anchor after declared ten guards/two oracle repairs; classify new ten identity sites."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2866_cleanup_identity553_fixed_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);a=load(i/'2827_master_target543_static_admission.json');old=load(r/a['static']['path']);repairpath=b/'evidence/PG32014-cleanup-identity-five-main-two-oracle-repair-v1/formatted-repair-proof.json';repair=load(repairpath);assert repair['actualExit']==0 and len(repair['sourcePins'])==7;changed=repair['sourcePins'];prior=collections.defaultdict(list)
for x in a['sourceAnchors']:
 path=x['path']
 if path in changed:
  assert sha(r/path)==changed[path]['formattedSourceSha256'] and old['inputHashes'][path]==changed[path]['originalSha256'] and changed[path]['inverseDeclaredCorrectionTokensExact']
 else:assert sha(r/path)==old['inputHashes'][path]
 prior[(path,x['rule'],x['sourceAnchor'],x['message'])].append(x)
newtest=next(x['path'] for x in pf['testSources'] if x['path'].endswith('/MigrationCleanupIdentityTest.java'));newad=load(i/'2865_cleanup_identity_repro_static_admission.json');newstatic=load(r/newad['static']['path']);assert sha(r/newtest)==newstatic['inputHashes'][newtest]
for x in newad['sourceAnchors']:
 if x['path']==newtest:prior[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
assert sum(map(len,prior.values()))==281
rows=[];counts=collections.Counter();rebound=0
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message'])
 if raw['rule']=='CompareObjectsWithEquals':
  assert path in changed and '/main/' in path and anchor=='if (cleanup != primary) primary.addSuppressed(cleanup);'
  reason='Throwable.addSuppressed prohibits adding the identical primary object as its own suppression. This exact reference identity guard preserves original SQL/runtime/Error failures; different exception objects remain suppressed even when their equals values match. Independent tests cover all five classes, mixed inner/outer aliases, result-close origin and duplicate distinct cleanup identities.';counts['selfIdentity']+=1
  row=dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE')
 else:
  assert prior[key],(path,raw['rule'],line,anchor);oldrow=prior[key].pop(0);row=dict(oldrow,sourceLine=line)
  if path in changed:
   row['reason']+=' Revalidated exact current anchor/rule/message after only the independently inverse-token-proven ten identity guards or two approved-primary oracle corrections; formatted repair proof SHA256 '+sha(repairpath)+'.';rebound+=1
  counts['revalidatedPrior']+=1
 rows.append(row)
assert not any(prior.values()) and counts==dict(revalidatedPrior=281,selfIdentity=10) and len(rows)==291
(i/'2867_cleanup_identity553_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,exactPrior281=True,changedSourceAnchorsIndividuallyRevalidated=rebound,newIdentityGuards=10,applicable=0,unclassified=0))
