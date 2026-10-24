"""Independent original host-only connection PT receipts; deliberately no Main coverage claim."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import scoped_prometheus_post as post
from host_tool_invocation import capture, verify


def execute(caller, original, run, slot, out, raw_sha, session_id, expected):
    host = post.host
    invocations = [capture(Path(caller)), capture(Path(__file__))]
    assert run.name == 'pg' + session_id.split('-')[0][2:] + '-' + run.name.split('-',1)[1]
    assert str(run).startswith(str(host.W)+'/') and str(slot).startswith(str(host.W)+'/')
    assert str(out).startswith(str(host.BASE)+'/') and slot.name.upper() == out.name.upper()
    assert run != slot and not slot.exists() and not out.exists()
    assert host.sha(run/'manifest.safe.json') == raw_sha
    raw = json.loads((run/'manifest.safe.json').read_text())
    post.common.SOURCE = original.SOURCE
    post.COUNTS = original.COUNTS
    post.assess(raw)
    assert host.sha(original.COMPILE/'manifest.safe.json') == original.COMPILE_SHA
    normal = json.loads((original.COMPILE/'manifest.safe.json').read_text())
    assert normal['source']==original.SOURCE and normal['actualExit']==normal['terminal']['actualExit']==0 and normal['testsExecuted']==0
    assert raw['begin']['sourceHashes']==normal['begin']['inputHashes']
    assert subprocess.check_output(['git','diff','--name-only',original.SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    for path,digest in normal['begin']['inputHashes'].items():
        assert host.sha(host.ROOT/path)==host.sha(original.COMPILE/'snapshot'/path)==digest
    for key in ('dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes'):
        assert all(host.sha(Path(path))==digest for path,digest in raw['begin'][key].items())
    assert host.sha(run/'jacoco.exec') == raw['execSha256']
    cases=[]
    for path in sorted((run/'xml').glob('TEST-*.xml')):
        assert host.sha(path)==raw['xmlHashes'][path.name]
        suite=ET.parse(path).getroot()
        assert raw['suites'][suite.get('name')]=={key:int(suite.get(key,'0')) for key in ('tests','failures','errors','skipped')}
        for case in suite.findall('testcase'):
            assert not list(case)
            cases.append((case.get('classname'),case.get('name')))
    assert len(cases)==len(set(cases))==len(expected) and set(cases)==set(expected)=={(row['classname'],row['name']) for row in raw['cases']}
    for stage,name in zip(raw['stages'],('fresh-test-compile.log','selected-junit.log')):
        assert stage['actualExit']==0 and stage['timedOut'] is False and host.sha(run/name)==stage['logSha256']
    log=(run/'selected-junit.log').read_text()
    environment={}
    for key in ('runtime.version','os.name','os.arch','os.version'):
        values=[line.split('=',1)[1] for line in log.splitlines() if line.startswith(key+'=')]
        assert len(values)==1 and values[0]
        environment[key]=values[0]
    assert environment['runtime.version'].startswith('25.0.4+') and environment['os.name']=='Linux'
    assert raw['begin']['environment']==post.common.ENV
    assert '-javaagent:'+str(post.common.AGENT)+'=destfile='+str(run/'jacoco.exec')+',append=false,sessionid='+session_id in raw['stages'][1]['command']
    rejected=[]
    for name,mutate in (
        ('source-tail',lambda r:r.update(source=post.different_source_tail(r['source']))),
        ('failed-case',lambda r:r['cases'][0].update(result='NOT_PASS')),
        ('duplicate-case',lambda r:r['cases'].__setitem__(1,copy.deepcopy(r['cases'][0]))),
        ('fixture-change',lambda r:r['begin'].update(fixtureHashes={'unknown':'0'*64})),
        ('coverage-union',lambda r:r['begin'].update(priorCoverageTransferred=True)),
        ('formal-inflation',lambda r:r.update(formalUpdated=True)),
        ('timeout-pass',lambda r:r['stages'][1].update(timedOut=True))):
        candidate=copy.deepcopy(raw)
        mutate(candidate)
        try:
            post.assess(candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError('every metadata guard rejects')
    core=host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    assert host.sha(core)=='ade1e0fdb4cd80d8537b57c6edb70a1360c47fdc518c20c65314517479bc4d0d'
    slot.mkdir()
    classes=slot/'reader'
    classes.mkdir()
    post.SLOT=slot
    helper=host.ROOT/'tools/quality/architecture/MetricCoexistenceSessionAudit.java'
    jdk=host.TC/'jdk-25.0.4/bin'
    compiled,_=post.step('session-reader-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',str(core),'-d',str(classes),str(helper)])
    assert compiled['actualExit']==0 and compiled['timedOut'] is False
    checked,output=post.step('original-session-metadata',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+str(core),'MetricCoexistenceSessionAudit',str(run/'jacoco.exec'),session_id])
    assert checked['actualExit']==0 and checked['timedOut'] is False
    session=[line.split('\t') for line in output.splitlines() if line.startswith('SESSION\t')]
    assert len(session)==1 and len(session[0])==5 and session[0][1]==session_id and int(session[0][4])>0
    foreign,foreign_output=post.step('foreign-session-rejected',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+str(core),'MetricCoexistenceSessionAudit',str(run/'jacoco.exec'),session_id+'-FOREIGN'])
    assert foreign['actualExit']==1 and foreign['timedOut'] is False and 'SESSION\t' not in foreign_output
    assert host.sha(run/'jacoco.exec')==raw['execSha256']
    for invocation in invocations:
        verify(invocation)
    out.mkdir()
    value=dict(actualExit=0,source=original.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocations=invocations,originalManifestSha256=raw_sha,normalManifestSha256=original.COMPILE_SHA,normalCompileReplayed=False,tests=len(cases),suites=len(original.COUNTS),failed=0,errors=0,skipped=0,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],actualEnvironment=environment,actualSessions=1,sessionMetadata=session[0],sessionReader=dict(sourceSha256=host.sha(helper),coreSha256=host.sha(core),compileReceipt=compiled,receipt=checked,foreignRejected=foreign,targetInitialized=False),newNegativeGuards=rejected,productionSourceChanged=False,newProductionClasses=0,coverageQualified=False,staticQualificationAdded=False,coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByPost=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(out/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=len(cases),suites=len(original.COUNTS),coverageQualified=False,manifestSha256=host.sha(out/'manifest.json'))))
