"""Bind already-reviewed unchanged Main anchors and two explicit new fixture findings only."""
from pathlib import Path
from collections import Counter
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=json.loads((b/'input/4409_ssc446_profile_v2.json').read_text());sp=r/c['slots']['static']/'manifest.json';st=json.loads(sp.read_text());prior=json.loads((b/'input/4349_ssc445_static_admission.json').read_text());anchors=prior['sourceAnchors']
test=c['testSources'][0]['path'];new=[dict(path=test,rule='UseConcurrentHashMap',sourceAnchor='Map<T, String> keys = new HashMap<>();',reason='This invocation-local map is never shared or published and deliberately tests actual equality/hash key retrieval on immutable records; there is no concurrent access.'),dict(path=test,rule='EqualsNull',sourceAnchor='assertFalse(first.equals(null));',reason='Intentional negative public value contract requiring equality false for null. This is a test assertion, not production null comparison logic.')]
rows=[];counts=Counter((x['path'],x['rule'],int(x['line']),x['message']) for x in st['rawFindings'])
for (path,rule,line,message),multiplicity in counts.items():
 rel=str(Path(path).relative_to(r));source=(r/rel).read_text().splitlines()[line-1].strip();matches=[a for a in anchors+new if a['path']==rel and a['rule']==rule and a['sourceAnchor']==source]
 assert len(matches)==1,dict(path=rel,rule=rule,line=line,source=source,candidates=len(matches))
 a=matches[0];rows.append(dict(path=rel,rule=rule,sourceAnchor=source,occurrences=1,sourceLine=line,rawMultiplicity=multiplicity,message=message,reason=a['reason'],disposition='NOT_APPLICABLE'))
v=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows)
(b/'input/4413_ssc446_static_admission_v2.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=len(st['rawFindings']),concreteAnchors=len(rows))))
