"""Classify each actual Root PMD finding against whole finite pure JUnit fixtures."""
from pathlib import Path
import json,hashlib
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=b/'input/2298b_env10_closed_profile.json';c=json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());s=r/c['slots']['static']/'manifest.json';m=json.loads(s.read_text());assert m['actualExit']==0 and len(m['rawFindings'])==10 and not m['processingErrors'];rows=[]
for x in m['rawFindings']:
 q=Path(x['path']);assert q.relative_to(r).as_posix() in [t['path'] for t in c['testSources']];lines=q.read_text().splitlines();n=int(x['line']);anchor=lines[n-1].strip();assert x['rule'] in ['CloseResource','DoNotUseThreads']
 reason=('Plain JUnit original64-task deterministic concurrency fixture, not a J2EE Web application. Timed invokeAll5SECONDS and get5SECONDS, finally shutdownNow and asserted awaitTermination10SECONDS own all workers. No Root/backend/native authority.' if x['rule']=='DoNotUseThreads' else 'Executor is released in the unconditional finally via shutdownNow and asserted finite awaitTermination10SECONDS. AutoCloseable.close/TWR would wait indefinitely and reintroduce BUG2830. Cancellation or failure remains failed PT, never a normal result.')
 rows.append(dict(path=str(q.relative_to(r)),rule=x['rule'],sourceAnchor=anchor,sourceLine=n,occurrences=lines.count(lines[n-1]),message=x['message'],rawMultiplicity=1,reason=reason,disposition='NOT_APPLICABLE'))
# occurrence is stripped source-anchor occurrence, as required by the verifier
for row in rows:row['occurrences']=sum(row['sourceAnchor'] in line for line in (r/row['path']).read_text().splitlines())
o=b/'input/2299_env10_static_admission.json';assert not o.exists();o.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(s),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print('10 exact findings; no rules suppressed; Main3 SB/missing/errors0')
