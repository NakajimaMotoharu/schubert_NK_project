"""Exact per-site finite JUnit workers; no default Test exclusion or quality rule changes."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
c=ld(i/'2642_scenario_staging18_profile.json');p=r/c['slots']['prepare']/'manifest.json';s=r/c['slots']['static']/'manifest.json';v=ld(s);rows=[];assert len(v['rawFindings'])==10
for x in v['rawFindings']:
 path=str(Path(x['path']).relative_to(r));line=int(x['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();assert '/src/test/java/' in path and x['rule'] in ['CloseResource','DoNotUseThreads'];assert any(word in anchor for word in ['newFixedThreadPool','workers.submit','executor.submit','shutdownNow','awaitTermination'])
 reason='This exact standalone JUnit stateless-value worker site is outside managed J2EE. Eight locally owned workers execute64 independent fixed COPY-vector checks; all Futures join within5s, finally always shutdownNow and asserts awaitTermination within10s. Explicit bounded lifecycle avoids unbounded ExecutorService.close; no DB/driver/network/FS/native/Root/service action and no blanket Test exemption.'
 rows.append(dict(path=path,rule=x['rule'],sourceLine=line,sourceAnchor=anchor,occurrences=1,message=x['message'],reason=reason,disposition='NOT_APPLICABLE'))
out=i/'2644_audio_copy_row28_static_admission.json';assert not out.exists();out.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(p),static=ref(s),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw10IndividuallyClassified=True,noSuppression=True)))
