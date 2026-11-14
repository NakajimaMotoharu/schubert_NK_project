"""Explicit per-site owned finite JUnit worker applicability, never a blanket Test exclusion."""
from pathlib import Path
import collections,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));ld=lambda p:json.loads(p.read_text())
pf=ld(i/'2593_file_copy_batch38_fixed_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=ld(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
assert collections.Counter(x['rule'] for x in s['rawFindings'])==dict(CloseResource=3,DoNotUseThreads=12) and not any('/main/' in x['path'] for x in s['rawFindings'])
anchors=[]
for test in pf['testSources']:
 path=test['path'];text=(r/path).read_text();assert 'Executors.newFixedThreadPool(8)' in text and 'index < 64' in text and 'future.get(5, TimeUnit.SECONDS)' in text and 'finally {' in text
 owners=re.findall(r'var (\w+) = Executors.newFixedThreadPool\(8\);',text);assert len(owners)==1;owner=owners[0];assert owner+'.shutdownNow();' in text
 assert re.search(r'assertTrue\('+owner+r'\.awaitTermination\(10, TimeUnit\.SECONDS\)(?:, "[^"\n]+")?\);',text)
 raw=[x for x in s['rawFindings'] if x['path']==str(r/path)];assert len(raw)==5
 for x in raw:
  line=int(x['line']);anchor=text.splitlines()[line-1].strip();assert text.count(anchor)==1
  reason=('The exact JUnit-owned executor is acquired before try and every exit executes finally shutdownNow and asserted awaitTermination10; all64 Future joins are bounded5. Implicit ExecutorService.close would not express this finite postcondition.' if x['rule']=='CloseResource' else 'This exact standalone pure-data JUnit site is not a J2EE managed webapp. Eight locally owned workers validate64 independent literal mapping/COPY results, each Future5 and finallyshutdownNow/await10 checked. No actual DB, filesystem, process, native or Root operation participates.')
  anchors.append(dict(path=path,rule=x['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=x['message'],reason=reason,disposition='NOT_APPLICABLE'))
p=i/'2594_file_copy_batch38_static_admission.json';assert not p.exists();p.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=anchors),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=15,perSiteReviewed=15,applicable=0,unclassified=0,sourceSuppressions=0)))
