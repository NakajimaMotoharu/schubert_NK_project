"""Three explicit original-fixture diagnostics, no blanket test or rule suppression."""
from pathlib import Path
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pp=b/'evidence/PG36990-checkpoint16-prepare-static-v1/manifest.json';p=json.loads(pp.read_text())
assert p['actualExit']==0 and p['expectedTests']==16 and not p['processingErrors'] and len(p['rawFindings'])==3
rows=[]
for x in p['rawFindings']:
    path=x['path'];text=(r/path).read_text();assert sha(r/path)==p['testSourceHashes'][path]
    anchor=text.splitlines()[int(x['beginline'])-1].strip()
    if x['rule']=='NullAssignment':
        assert anchor=='if (fault.equals("null")) agent.bytes = null;'
        reason='NCHECK193003: this exact assignment deliberately supplies the missing byte array to the memory Agent fixture. The independent assertions require fixed IOException/no cause and zero exports/data replay; removing null would remove the API-boundary negative test. No production invariant is weakened.'
    else:
        assert x['rule']=='DoNotUseThreads' and any(a in anchor for a in ['Executors.newFixedThreadPool(4)','pool.submit('])
        assert 'result.get(5, TimeUnit.SECONDS)' in text and 'try (var pool = Executors.newFixedThreadPool(4)) {' in text and 'n < 32' in text
        reason='NCHECK193006: standalone own-JVM fixed4-worker32-task memory export fixture; every Future has5s get and Java25 try-with-resources owns pool.close; all32 tasks contain only bounded memory operations, and the owned whole JUnit JVM has120s outer termination budget. Exact PMD warning explicitly assumes J2EE-managed webapp, whereas SS311/342 is direct Java. This classification proves applicability only, not a running backend or parent lifecycle.'
    rows.append(dict(raw=x,sourceSha256=sha(r/path),sourceAnchor=anchor,disposition='NOT_APPLICABLE',reason=reason))
assert len([x for x in rows if x['raw']['rule']=='NullAssignment'])==1
out=b/'evidence/PG36992-checkpoint16-static-admission-v1';assert not out.exists();out.mkdir()
(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,source=p['source'],terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=dict(path=str(pp.relative_to(r)),sha256=sha(pp)),sourceInputs=p['testSourceHashes'],raw=3,applicable=0,unclassified=0,classified=rows,newSuppressions=0,rootRulesChanged=False,productTestsExecuted=0,formalUpdated=False),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,raw=3,applicable=0,unclassified=0,productTests=0)))
