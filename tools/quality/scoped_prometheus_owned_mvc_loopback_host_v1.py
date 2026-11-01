"""Reviewed own loopback HTTP fixture only. Same original source/selection/terminal gates, explicit effects."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import pg6966_chr_adapter_host as host
import pg8122_web_pool_six_compile as compilation
from host_tool_invocation import capture, verify

COMPILE=compilation.SLOT
SOURCE='e196d0816c8a4920696d4f601f8b4cf97e9e8b48'
COMPILE_SHA='75ca9dd88ce045dc0acdbdd878e9382a30584a1da34fb8d37bc04d2ca4d4a53b'
SDK_FILE=host.BASE/'PG8170-prometheus-sdk-prepare-v1/manifest.json'
SDK_SHA='371004a7bcadce5d398059e765ef8f3dc876a7ea004fced60ba8ceb05fad123a'
SDK_POST=host.BASE/'PG8173-prometheus-sdk-exact-source-post-v1/manifest.json'
SDK_POST_SHA='a5a2bfbe93bf8b8cc9521b67d1ce4a4c540bc967d7814927b0417807c6b30572'
SLOT=host.W/'pg8178-web-prometheus-gauge-host-v1'
OUT=host.BASE/'PG8178-web-prometheus-gauge-host-v1'
LAUNCHER=host.TC/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
LAUNCHER_SHA='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
AGENT=host.TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
HELPER=host.ROOT/'tools/quality/architecture/WebPrometheusGaugeJunitLauncher.java'
NEW_TEST=host.ROOT/'tools/quality/architecture/WebPrometheusGaugeContractTest.java'
SESSION_ID='PG8178-WEB-PROMETHEUS-GAUGE'
FIXTURE='src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
FIXTURE_SHA='1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'
COUNTS={}
TEST_ROOT=host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
FIXTURES={}
EXTRA_TEST_SOURCES=()
TEST_SOURCE_OVERRIDES={}
ENV={'PATH':str(host.TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','LANG':'C.UTF-8'}


def require(value,message):
    if not value:
        raise ValueError(message)


def step(name,command):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    require(not (SLOT/(name+'-begin.safe.json')).exists(),'new-only own step; no unknown replay')
    host.write(SLOT/(name+'-begin.safe.json'),dict(command=command,startUTC=start,environment=ENV))
    with (SLOT/(name+'.log')).open('xb') as log:
        child=subprocess.Popen(command,cwd=SLOT,env=ENV,stdin=subprocess.DEVNULL,
                               stdout=log,stderr=subprocess.STDOUT,close_fds=True)
        host.write(SLOT/(name+'-process.safe.json'),dict(pid=child.pid,ownerPid=os.getpid(),
                   command=command,cwd=str(SLOT),startUTC=start))
        timed_out=False
        try:
            code=child.wait(timeout=180)
        except subprocess.TimeoutExpired:
            timed_out=True
            child.kill()
            code=child.wait(timeout=15)
        log.flush()
        os.fsync(log.fileno())
    row=dict(command=command,startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             actualExit=code,timedOut=timed_out,logSha256=host.sha(SLOT/(name+'.log')))
    host.write(SLOT/(name+'-exit.safe.json'),row)
    return row


OWNED_LOOPBACK_AUTHORITY=False

def loopback_effects():
    require(OWNED_LOOPBACK_AUTHORITY is True and SOURCE=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',
            'explicit reviewed host-only fixture contract, never OS or production authority')
    require(COUNTS=={'WebHttpServerTest':12,'WebHttpAdmissionTest':3},
            'only whole original reviewed fifteen; held child tests not authorized')
    require(NEW_TEST==host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServerTest.java'
            and TEST_ROOT==NEW_TEST.parent and TEST_SOURCE_OVERRIDES=={} and FIXTURES=={},
            'fixed original test source paths, no extracted cases or alternate fixture')
    return dict(actualNetworkActions=None,networkOperationCountStatus='NOT_MEASURED_NOT_ZERO',
                declaredOwnedLoopbackFixtureNetwork=True,declaredLoopbackAddresses=['127.0.0.1'],
                declaredLoopbackPorts='EPHEMERAL_OR_PRIOR_SELF_OWNED_REBIND',
                actualExternalNetworkActions=0,actualProductionServiceActions=0,
                effectAuthority='SELF_OWNED_UNIT_TEST_HTTP_FIXTURE_NOT_PRODUCTION_BUSINESS_START_OR_OS_ADMISSION')

def main():
    effects=loopback_effects()
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only original JVM; existing run is never replayed')
    require(host.sha(COMPILE/'manifest.safe.json')==COMPILE_SHA,'immutable original normal compile witness')
    raw=json.loads((COMPILE/'manifest.safe.json').read_bytes())
    snapshot=COMPILE/'snapshot'
    require(raw['source']==SOURCE and raw['actualExit']==raw['terminal']['actualExit']==0
            and raw['testsExecuted']==0,'normal compile-only, never historical PT transfer')
    source_hashes=raw['begin']['inputHashes']
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in source_hashes.items()),
            'all normal frozen input bytes equal current production inputs')
    require(host.sha(SDK_FILE)==SDK_SHA and host.sha(SDK_POST)==SDK_POST_SHA,'exact prepared SDK and independent post witnesses')
    sdk=json.loads(SDK_FILE.read_bytes())
    require(sdk['actualExit']==0 and sdk['newJarCount']==10 and sdk['existingJarCount']==5,'fixed reviewed SDK bundle')
    sdk_jars={row['jar']['path']:row['jar']['sha256'] for row in sdk['downloaded'].values()}
    sdk_jars.update({row['path']:row['sha256'] for row in sdk['reused'].values()})
    require(len(sdk_jars)==15 and all(host.sha(Path(p))==h for p,h in sdk_jars.items()),'all prepared SDK byte pins')
    require(host.sha(LAUNCHER)==LAUNCHER_SHA and AGENT.is_file(),'official existing JUnit and agent')
    cpfile=snapshot/'src/schubert-nk-web/target/pgpt-test-classpath.txt'
    dependencies=[Path(p) for p in cpfile.read_text().strip().split(os.pathsep)]
    external=[p for p in dependencies if '/dev/codex/schubert/' not in str(p)
              and not str(p).startswith(str(snapshot)+'/src/')]
    require(external and all(p.is_file() and str(p).startswith(str(host.TC/'m2/repository')+'/')
                            for p in external),'only actual normal external libraries, no stale internal M2')
    jars=[]
    for item in raw['jars'].values():
        p=Path(item['path'])
        require(host.sha(p)==item['sha256'],'same normal six Main Jar bytes')
        jars.append(p)
    annotation=host.TC/'m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'
    require(host.sha(annotation)=='766ad2a0783f2687962c8ad74ceecc38a28b9f72a2d085ee438b7813e928d0c7',
            'existing compile annotation pin')
    inputs=list(dict.fromkeys([*jars,*external,*[Path(p) for p in sdk_jars],LAUNCHER,annotation]))
    require(set(TEST_SOURCE_OVERRIDES) <= (set(COUNTS)-{NEW_TEST.stem}),
            'only declared selected test source overrides')
    selected=[TEST_SOURCE_OVERRIDES.get(n,TEST_ROOT/(n+'.java')) for n in COUNTS if n!=NEW_TEST.stem]
    test_sources=[*selected,NEW_TEST,HELPER,*EXTRA_TEST_SOURCES]
    require(all(p.is_file() for p in test_sources),'all declared fresh test sources and launcher')
    require(COUNTS and NEW_TEST.stem in COUNTS and all(type(n) is int and n>0 for n in COUNTS.values()),
            'caller freezes nonempty exact test count matrix')
    resources={}
    for relative,expected in FIXTURES.items():
        file=host.ROOT/relative
        data=subprocess.check_output(['git','show',SOURCE+':'+relative],cwd=host.ROOT)
        require(hashlib.sha256(data).hexdigest()==host.sha(file)==expected,'independent original/current fixture')
        resource_name=relative.split('/src/test/resources/',1)[1]
        require(not Path(resource_name).is_absolute() and '..' not in Path(resource_name).parts,'closed safe resource path')
        resources[resource_name]=(data,expected)
    os.umask(0o077)
    SLOT.mkdir()
    classes=SLOT/'fresh-test-classes'
    classes.mkdir()
    fixture_hashes={}
    for relative,(data,expected) in resources.items():
        destination=classes/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(data)
        require(host.sha(destination)==expected,'exact own independent fixture copy')
        fixture_hashes[str(destination)]=expected
    fixture_hashes.update({str(host.ROOT/p):h for p,h in FIXTURES.items()})
    for p in (classes/'prometheus.properties',SLOT/'empty-prometheus.properties'):
        with p.open('xb'):
            pass
    classpath=os.pathsep.join(str(p) for p in [classes,*inputs])
    begin=dict(source=SOURCE,qualificationHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
       compileManifestSha256=COMPILE_SHA,normalCompileReplayed=False,priorCoverageTransferred=False,
       archiveSha256=raw['begin']['archiveSha256'],sourceHashes=source_hashes,
       classpathFileSha256=host.sha(cpfile),dependencyHashes={str(p):host.sha(p) for p in [*inputs,AGENT]},
       sdkManifestSha256=SDK_SHA,sdkPostSha256=SDK_POST_SHA,
       testSourceHashes={str(p):host.sha(p) for p in test_sources},selectedSuites=COUNTS,expectedTests=sum(COUNTS.values()),
       fixtureHashes=fixture_hashes,fixtureSource=SOURCE,
       emptyConfigHashes={str(p):host.sha(p) for p in (classes/'prometheus.properties',SLOT/'empty-prometheus.properties')},
       invocation=invocation,environment=ENV,actualVmActions=0,actualDatabaseActions=0,
       actualServiceActions=0,rootMainInvoked=False,**effects,
       startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    host.write(SLOT/'begin.safe.json',begin)
    jdk=host.TC/'jdk-25.0.4/bin'
    stages=[step('fresh-test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
                                     '-cp',classpath,'-d',str(classes),*[str(p) for p in test_sources]])]
    if stages[0]['actualExit']==0:
        stages.append(step('selected-junit',[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
          '-Dprometheus.config='+str(SLOT/'empty-prometheus.properties'),
          '-javaagent:'+str(AGENT)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+SESSION_ID,
          '-cp',classpath,HELPER.stem,str(SLOT/'xml')]))
    suites={}
    cases=[]
    xml_hashes={}
    for path in sorted((SLOT/'xml').glob('TEST-*.xml')):
        root=ET.parse(path).getroot()
        name=root.get('name')
        simple=name.rpartition('.')[2]
        require(simple in COUNTS and name not in suites,'exact declared suites only')
        suites[name]={k:int(root.get(k,'0')) for k in ('tests','failures','errors','skipped')}
        xml_hashes[path.name]=host.sha(path)
        for case in root.findall('testcase'):
            cases.append(dict(classname=case.get('classname'),name=case.get('name'),
                        result='PASS' if not list(case) else 'NOT_PASS',nonPass=[c.tag for c in case]))
    code=stages[-1]['actualExit']
    if code==0:
        require(len(suites)==len(COUNTS) and len(cases)==sum(COUNTS.values()) and len({(c['classname'],c['name']) for c in cases})==sum(COUNTS.values())
                and all(row==dict(tests=COUNTS[n.rpartition('.')[2]],failures=0,errors=0,skipped=0)
                        for n,row in suites.items()) and all(c['result']=='PASS' for c in cases),
                'all declared actual cases; failed/skipped/not-run never PASS')
    require(all(host.sha(Path(p))==h for p,h in begin['dependencyHashes'].items()),'all actual dependency bytes unchanged')
    require(all(host.sha(Path(p))==h for p,h in begin['testSourceHashes'].items()),'fresh test source unchanged')
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in source_hashes.items()),
            'same source archive/current inputs after original run')
    require(all(host.sha(Path(p))==h for p,h in begin['emptyConfigHashes'].items()),'empty public configs unchanged')
    require(all(host.sha(Path(p))==h for p,h in begin['fixtureHashes'].items()),'independent fixture unchanged after run')
    verify(invocation)
    value=dict(source=SOURCE,actualExit=code,begin=begin,stages=stages,suites=suites,cases=cases,xmlHashes=xml_hashes,
         execSha256=host.sha(SLOT/'jacoco.exec') if (SLOT/'jacoco.exec').exists() else None,
         qualification='RAW_TERMINAL_ONLY_POST_PENDING',actualOwnedLoopbackNetworkExercised=code==0,
         actualNetworkScopeProof='ALL_EXPECTED_CASES_PASS_ASSERT_REAL_LOOPBACK_TRANSACTIONS' if code==0 else 'INCOMPLETE',
         whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    host.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir()
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=code,tests=len(cases),suites=len(suites),manifestSha256=host.sha(OUT/'manifest.json'))))
    raise SystemExit(code)
