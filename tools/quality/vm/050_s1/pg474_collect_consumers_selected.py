"""PG-D379: fresh selected JUnit signatures; accumulated exec is not whole/native acceptance."""
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import xml.etree.ElementTree as E

os.umask(0o077)
ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
version = sys.argv[1]
assert version in ('v3', 'v4', 'v5', 'v6')
stem = WORK / ('pg474-api-consumers-selected-' + version)
def read(suffix):
    return pathlib.Path(str(stem) + suffix).read_text().strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert read('.exit') == '0'
started = datetime.datetime.fromisoformat(read('.started')).timestamp()
completed = datetime.datetime.fromisoformat(read('.completed')).timestamp()
log = read('.log')
assert 'BUILD SUCCESS' in log
assert log.count('BugInstance size is 0') == 4
assert log.count('No errors/warnings found') == 4
expected = {
    'protocol': {'MessageCodecTest'},
    'storage': {'ResourceScopeTest', 'PrivateDirectoryEntryTest'},
    'bootstrap': {'FixedServiceIdentityTest', 'ServiceCredentialSetTest'},
    'api': {'ApiMessagingRuntimeTest', 'WebLogConsumersTest', 'SyncRequestConsumersTest',
            'QuestionWorkConsumersTest', 'ApiConsumerRemainderTest', 'ApiConsumerTerminalRemainderTest',
            'ApiBrokerContextsTest', 'ApiBrokerContextsCredentialTest', 'ApiBrokerFactoryRemainderTest'},
}
private = WORK / ('pg474-consumers-selected-' + version + '-frozen')
assert not private.exists()
private.mkdir(mode=0o700)
rows = []
for module, names in expected.items():
    for name in sorted(names):
        paths = list((ROOT / 'src' / ('schubert-nk-' + module) / 'target/surefire-reports').glob('TEST-*.' + name + '.xml'))
        assert len(paths) == 1
        path = paths[0]
        assert started <= path.stat().st_mtime <= completed + 1
        suite = E.parse(path).getroot()
        count = int(suite.get('tests'))
        assert count > 0 and all(int(suite.get(k)) == 0 for k in ('failures', 'errors', 'skipped'))
        cases = suite.findall('testcase')
        assert len(cases) == count
        assert all(not any(c.find(t) is not None for t in ('failure', 'error', 'skipped')) for c in cases)
        signature = re.search(r'Tests run: '+str(count)+r', Failures: 0, Errors: 0, Skipped: 0,.* -- in '+re.escape(suite.get('name')), log)
        assert signature
        shutil.copy2(path, private / path.name)
        (private / path.name).chmod(0o600)
        rows.append({'module':module, 'class':suite.get('name'), 'tests':count,
                     'xmlSha256':sha(path), 'methods':[c.get('name') for c in cases]})
assert len(rows) == 14
coverage = ROOT / 'src/schubert-nk-api/target/site/jacoco/jacoco.xml'
assert started <= coverage.stat().st_mtime <= completed + 1
shutil.copy2(coverage, private / 'api-accumulated.xml')
(private / 'api-accumulated.xml').chmod(0o600)
doc = E.parse(coverage).getroot()
counters = {}
for name in ['ApiBrokerContexts','ApiMessagingRuntime','WebLogConsumers','QuestionWorkConsumers','SyncRequestConsumers']:
    matches = [c for c in doc.findall('.//class') if c.get('name').rsplit('/',1)[-1] == name]
    assert len(matches) == 1
    counters[name] = {v.get('type'):{'missed':int(v.get('missed')), 'covered':int(v.get('covered'))} for v in matches[0].findall('counter')}
out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional' / ('PG474-api-consumers-selected-' + version)
assert not out.exists()
out.mkdir(parents=True)
payload = {'id':out.name, 'programId':['NK-MSG-001','NK-MSG-002','NK-ASY-001','NK-OPS-001'],
    'TestIDs':['PT-OPS-API-REM001..004','PT-OPS-API-FACT001'], 'PGD':'PG-D379',
    'baseCommit':read('.source'), 'branch':'dev-foundation', 'dirtySource':True,
    'started':read('.started'), 'completed':read('.completed'), 'actualExit':0,
    'command':'bash tools/quality/vm/050_s1/pg474_api_consumers_selected_' + version + '.sh',
    'tests':sum(r['tests'] for r in rows), 'suites':len(rows), 'F':0, 'E':0, 'S':0, 'XML':rows,
    'staticModules':4, 'staticFindings':0, 'formatNullAwayWerror':'PASS',
    'localCounters':counters, 'coverageXMLSha256':sha(coverage),
    'privateLogSha256':sha(pathlib.Path(str(stem)+'.log')),
    'sourceDiffSha256':sha(pathlib.Path(str(stem)+'.source-diff.private')),
    'sourceFilesSha256':sha(pathlib.Path(str(stem)+'.source-files.sha256')),
    'environment':{'OS':'Linux','JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15'},
    'independentOracle':'literal provider profile/order, Throwable identity, actual embedded broker golden wire/ACK/rollback; wrong-type provider object is rejection-only',
    'v1':{'actualExit':1,'API':'NOT_RUN','reason':'new draft JUnit conditional generic inference compile'},
    'v2':{'actualExit':0,'tests':81,'suites':13,'F':0,'E':0,'S':0,'staticModules':4,
          'privateLogSha256':sha(WORK/'pg474-api-consumers-selected-v2.log'),
          'XMLFrozen':False,'notReusedForV3':True},
    'accumulatedExec':True,'wholeCoverage100':False,'nativeAccepted':False,
    'formalUpdated':False,'oldNativeReused':False,'rawSecretsExported':False,'ITSTAccepted':False}
path = out / 'manifest.json'
with path.open('x') as stream:
    json.dump(payload,stream,ensure_ascii=False,indent=2)
    stream.write('\n')
print(json.dumps({'tests':payload['tests'],'suites':len(rows),'static4zero':True,
                  'manifestSha256':sha(path), 'localMiss':{n:{k:v['missed'] for k,v in cs.items() if k in ['BRANCH','LINE','METHOD','CLASS']} for n,cs in counters.items()},'formal':False}))
