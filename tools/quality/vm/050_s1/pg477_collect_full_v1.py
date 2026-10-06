"""PG-D382 fresh six-module same-source byte/XML freeze; no native/formal acceptance."""
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as E

os.umask(0o077)
ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
version = sys.argv[1]
assert version in ('v1', 'v2')
stem = WORK / ('pg477-six-full-' + version)
def read(suffix):
    return pathlib.Path(str(stem) + suffix).read_text().strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
SOURCE = read('.source')
assert re.fullmatch('[0-9a-f]{40}', SOURCE)
assert read('.exit') == '0'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() == SOURCE
subprocess.run(['git','diff','--exit-code',SOURCE,'--','src','tools','pom.xml'],cwd=ROOT,check=True)
subprocess.run(['sha256sum','--check','--status',str(stem)+'.source-files.sha256'],cwd=ROOT,check=True)
log = read('.log')
assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0') == 6
assert log.count('No errors/warnings found') == 6
started = datetime.datetime.fromisoformat(read('.started')).timestamp()
completed = datetime.datetime.fromisoformat(read('.completed')).timestamp()
frozen = WORK / ('pg477-host' if version == 'v1' else 'pg477-host-v2')
assert not frozen.exists()
frozen.mkdir(mode=0o700)
rows=[]
for module in ['protocol','storage','bootstrap','api','web','batch']:
    target = ROOT/'src'/('schubert-nk-'+module)/'target'
    copy = frozen/module
    shutil.copytree(target,copy)
    copy.chmod(0o700)
    for path in copy.rglob('*'):
        path.chmod(0o700 if path.is_dir() else 0o600)
        if path.is_file(): assert sha(path)==sha(target/path.relative_to(copy))
    reports=list((copy/'surefire-reports').glob('TEST-*.xml'))
    assert reports
    suiteRows=[]
    for path in reports:
        assert started <= path.stat().st_mtime <= completed + 1
        suite=E.parse(path).getroot()
        assert int(suite.get('tests')) > 0
        assert all(int(suite.get(k,'0'))==0 for k in ['failures','errors','skipped'])
        cases=suite.findall('testcase')
        assert len(cases)==int(suite.get('tests'))
        assert all(not any(c.find(t) is not None for t in ['failure','error','skipped']) for c in cases)
        suiteRows.append({'class':suite.get('name'),'tests':int(suite.get('tests')),'xmlSha256':sha(path)})
    xml=copy/'site/jacoco/jacoco.xml'
    assert started <= xml.stat().st_mtime <= completed + 1
    doc=E.parse(xml).getroot()
    counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in doc.findall('counter')}
    rows.append({'module':module,'suiteCount':len(reports),'tests':sum(s['tests'] for s in suiteRows),'FES':0,
                 'XML':suiteRows,'counters':counters,'coverageXmlSha256':sha(xml),
                 'projectJarSha256':sha(copy/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'))})
assert sum(r['tests'] for r in rows)==3378 and sum(r['suiteCount'] for r in rows)==507
api=E.parse(frozen/'api/site/jacoco/jacoco.xml').getroot()
closed={}
for name in ['ApiBrokerContexts','ApiMessagingRuntime','WebLogConsumers','QuestionWorkConsumers','SyncRequestConsumers','QuestionSubmissionService','InspectionRunExecutor','InspectorProcess']:
    matches=[c for c in api.findall('.//class') if c.get('name').endswith('/'+name)]
    assert len(matches)==1
    counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in matches[0].findall('counter')}
    assert all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH'])
    closed[name]=counters
bootstrap=E.parse(frozen/'bootstrap/site/jacoco/jacoco.xml').getroot()
profile=[c for c in bootstrap.findall('.//class') if c.get('name').endswith('/FixedNativeCoverageProfile')]
assert len(profile)==1
profileCounters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in profile[0].findall('counter')}
assert all(profileCounters[k]['missed']==0 and profileCounters[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH'])
closed['FixedNativeCoverageProfile']=profileCounters
payload={'id':'PG477-maintenance-terminal-full-' + version,'productionSource':SOURCE,'branch':'dev-foundation','actualExit':0,
    'started':read('.started'),'completed':read('.completed'),
    'command':'bash tools/quality/vm/050_s1/pg477_full_' + version + '.sh '+SOURCE,
    'modules':rows,'tests':3378,'suiteCount':507,'FES':0,'staticModules':6,'staticIssues':0,
    'formatNullAwayWerrorPassed':True,'sourceBeforeAfterUnchanged':True,'allFrozenBytesMatched':True,
    'closedConsumerClassCounters':closed,'PGD':'PG-D382','testIds':['PT-OPS-API-OWN001..004','PT-OPS-NC196001..004','PT-OPS-NC193/NCHECK193/NEXPORT193','all existing six-module PTs'],
    'globalCoverage100':False,'nativeSameSourceAccepted':False,'allChrPassed':False,'formalPass':False,
    'oldNativeReused':False,'ITSTAccepted':False,'rawLogsInGit':False,
    'logSha256':sha(pathlib.Path(str(stem)+'.log')),
    'sourceFilesSha256':sha(pathlib.Path(str(stem)+'.source-files.sha256')),
    'environment':{'jdk':'25.0.4','maven':'3.9.12','node':'24.19.0','jacoco':'0.8.15'}}
out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/('PG477-maintenance-terminal-full-' + version)/'manifest.json'
assert not out.exists()
out.parent.mkdir(parents=True)
with out.open('x') as stream:
    json.dump(payload,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'tests':3378,'suites':507,'static6zero':True,'sameSourceBytes':True,
                  'closedConsumerCounters':True,'coverage100':False,'formal':False,'manifestSha256':sha(out)}))
