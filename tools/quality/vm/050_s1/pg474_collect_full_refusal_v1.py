"""Preserve the immutable first full run and its actual coverage rejection, never PASS."""
import hashlib
import json
import pathlib
import xml.etree.ElementTree as E

R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert (W/'pg474-six-full-v1.source').read_text().strip()=='abdb6f35a008f7e92f189ba7488856cf7c0ddc57'
assert (W/'pg474-six-full-v1.exit').read_text().strip()=='0'
log=(W/'pg474-six-full-v1.log').read_text()
assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0')==6
rows=[]
for m in ['protocol','storage','bootstrap','api','web','batch']:
    t=W/'pg474-host'/m
    reports=list((t/'surefire-reports').glob('TEST-*.xml'))
    suites=[E.parse(p).getroot() for p in reports]
    assert suites and all(int(s.get(k,'0'))==0 for s in suites for k in ['failures','errors','skipped'])
    rows.append({'module':m,'tests':sum(int(s.get('tests')) for s in suites),'suites':len(suites),
                 'FES':0,'coverageXmlSha256':sha(t/'site/jacoco/jacoco.xml')})
assert sum(r['tests'] for r in rows)==3365 and sum(r['suites'] for r in rows)==505
report=E.parse(W/'pg474-host/api/site/jacoco/jacoco.xml').getroot()
cls=report.find("./package[@name='dev/codex/schubert/nk/api/messaging/inbound']/class[@name='dev/codex/schubert/nk/api/messaging/inbound/SyncRequestConsumers']")
assert cls is not None
counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in cls.findall('counter')}
assert counters['LINE']['missed']==2 and counters['BRANCH']['missed']==0
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG474-full-v1-coverage-refused/manifest.json'
assert not out.exists()
out.parent.mkdir(parents=True)
payload={'id':out.parent.name,'productionSource':'abdb6f35a008f7e92f189ba7488856cf7c0ddc57',
    'branch':'dev-foundation','started':(W/'pg474-six-full-v1.started').read_text().strip(),
    'completed':(W/'pg474-six-full-v1.completed').read_text().strip(),
    'command':'bash tools/quality/vm/050_s1/pg474_full_v1.sh abdb6f35a008f7e92f189ba7488856cf7c0ddc57',
    'buildTestScriptActualExit':0,'tests':3365,'suites':505,'F':0,'E':0,'S':0,
    'staticModules':6,'staticFindings':0,'modules':rows,'consumerCounters':counters,
    'qualityCollectorActualExit':1,'qualityAccepted':False,'globalCoverage100':False,
    'reason':'fresh Sync consumer normal rollback missed LINE80/83; accumulated selected exec had masked missing fixture',
    'BUG':'BUG-762','YKT':'YKT-542','TestIDs':['PT-OPS-API-REM004'],
    'privateLogSha256':sha(W/'pg474-six-full-v1.log'),
    'sourceFilesSha256':sha(W/'pg474-six-full-v1.source-files.sha256'),
    'environment':{'OS':'Linux','JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','Node':'24.19.0'},
    'rawSecretsInGit':False,'nativeAccepted':False,'formalUpdated':False,'ITSTAccepted':False}
with out.open('x') as f: json.dump(payload,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'tests':3365,'suites':505,'static6zero':True,'qualityAccepted':False,'manifestSha256':sha(out)}))
