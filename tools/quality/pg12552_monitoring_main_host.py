"""Affected whole21 pure metadata PT, no Root/Unit/DB/native/service operations."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as steps

SOURCE='fb1a22da2433c7909ceba05c7eeb07c879e52325'
NORMAL_SHA='a51e4812b19c20f1ef673b35278a9c4ef75e08100e785360033bbd5c1afdc5e0'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12552-monitoring-main-host-v1'
OUT=data.BASE/'PG12552-monitoring-main-host-v1'
PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/'
COUNTS=dict(MetricContractTest=6,MonitoringModePolicyTest=7,MonitoringRetentionConfigurationTest=8)


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    np=data.BASE/'PG12551-monitoring-main-six-compile-v2/manifest.json';normal=data.read_checked(np,NORMAL_SHA)
    plan=data.read_checked(data.BASE/'PG12548-monitoring-main-plan-v1/manifest.json','e1b73f8dda2d18379ba8edcf172709a520dab816d33a94458d90bffbd3157baf')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    assert plan['actualExit']==0 and plan['mainCorrections']==6 and plan['metadataNegativeVectors']==11
    hashes=normal['begin']['inputHashes'];snapshot=Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    changes={x['path']:x['sha256'] for x in plan['sourceChanges']};assert all(hashes[p]==h for p,h in changes.items())
    for p in changes:
        text=(snapshot/p).read_text()
        assert not any(w in text for w in ('java.nio.file','java.net.','java.sql.','ProcessBuilder','ServiceLoader','Class.forName','JMSContext','getRuntime('))
    helper=data.ROOT/'tools/quality/architecture/MonitoringMainJunitLauncher.java';helpertext=helper.read_text()
    assert 'EXPECTED_TESTS = 21;' in helpertext and 'EXPECTED_SUITES = 3;' in helpertext
    assert not any(w in helpertext for w in ('Class.forName','selectPackage(','scanClasspath'))
    cases=[]
    for name,count in COUNTS.items():
        p=PREFIX+name+'.java';text=(snapshot/p).read_text()
        assert not any(w in text for w in ('@Before','@After','@ExtendWith','@Disabled','@TempDir','java.nio.file','Files.','Path.of','java.net.','java.sql.','ProcessBuilder','System.getenv','System.getProperty','getConnection(','TemporaryInfrastructureException','WebStartupException','setAccessible'))
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods)==len(set(methods))==count
        for method in methods:
            binary='dev.codex.schubert.nk.batch.monitoring.'+name
            assert binary+'#'+method in helpertext
            cases.append(dict(className=binary,method=method,path=p,sourceSha256=hashes[p]))
    rp='src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv'
    rout=snapshot/'src/schubert-nk-batch/target/test-classes/monitoring/metric-catalog.tsv'
    assert data.sha(rout.read_bytes())==hashes[rp]
    tc=data.ROOT.parent/'toolchain';cwd=snapshot/'src/schubert-nk-batch'
    libraries=list(dict.fromkeys((cwd/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep)))
    jars={k:v['path'] for k,v in normal['jars'].items()};assert len(jars)==len(set(jars.values()))==6
    launcher=tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    assert data.sha(launcher.read_bytes())=='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    deps={str(p):data.sha(Path(p).read_bytes()) for p in [*jars.values(),*libraries,launcher,agent]}
    physical={str(p):data.sha(p.read_bytes()) for p in (cwd/'target/test-classes').rglob('*.class')}
    os.umask(0o077);SLOT.mkdir();testcwd=SLOT/'test-cwd';testcwd.mkdir();reader=SLOT/'launcher';reader.mkdir()
    catalog=SLOT/'frozen-methods.tsv'
    with catalog.open('x') as f:f.write(''.join(r['className']+'\t'+r['method']+'\n' for r in cases))
    entries=list(dict.fromkeys(map(str,[reader,cwd/'target/test-classes',*jars.values(),*libraries,launcher])))
    assert set(jars.values())<=set(entries)
    locations=[]
    for entry in entries:
        p=Path(entry)
        if p.is_dir():
            if (p/'monitoring/metric-catalog.tsv').is_file():locations.append(str(p))
        elif p.suffix=='.jar':
            with zipfile.ZipFile(p) as jar:
                if 'monitoring/metric-catalog.tsv' in jar.namelist():locations.append(str(p))
    assert locations==[str(cwd/'target/test-classes')]
    cp=os.pathsep.join(entries);hh=data.sha(helper.read_bytes())
    begin=dict(source=SOURCE,invocation=invocation,sourceInputHashes=hashes,normalManifestSha256=NORMAL_SHA,dependencyHashes=deps,physicalTestFiles=physical,helperPath=str(helper),helperSha256=hh,cases=cases,expectedMethods=21,expectedSuites=3,normalSnapshot=str(snapshot),testCwd=str(testcwd),moduleJars=jars,classpath=cp,resource=dict(path=rp,sha256=hashes[rp],uniqueDefinition=locations),eligibilityClosureSourceHashes=changes,judgement='PT_DEFAULT_PURE_JDK_IMMUTABLE_ENUM_AND_OWN_FINITE_WORKERS_PUBLIC_TSV_NO_SERVICE_IO')
    data.write(SLOT/'begin.safe.json',begin);steps.SLOT=SLOT
    stages=[steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    actual=[];xmls={};session='PG12552-MONITORMAIN-JP';code=stages[0]['actualExit']
    if code==0 and not stages[0]['timedOut']:
        command=[str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,'-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('pure-monitoring-main-jp',command,testcwd,timeout=240))
        for f in sorted((SLOT/'xml').glob('TEST-*.xml')):
            node=ET.parse(f).getroot();xmls[f.name]=data.sha(f.read_bytes())
            actual.extend(dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in node.findall('testcase'))
        passed=stages[-1]['actualExit']==0 and not stages[-1]['timedOut'] and len(xmls)==3 and len(actual)==21 and Counter((r['classname'],r['name']) for r in actual)==Counter((r['className'],r['method']) for r in cases) and not any(r['nonPass'] for r in actual)
        code=0 if passed else stages[-1]['actualExit'] or 1
    else:code=code or 1
    assert not list(testcwd.iterdir()) and data.sha(helper.read_bytes())==hh
    assert all(data.sha(Path(p).read_bytes())==h for p,h in {**deps,**physical}.items())
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation)
    value=dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,sessionId=session,observedTestExecutions=len(actual),execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()) if (SLOT/'classload-metadata.log').exists() else None,oldExecUnion=False,coveragePendingIndependentPost=True,newAccepted=0,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value);OUT.mkdir();data.write(OUT/'manifest.json',value)
    for f in (SLOT/'xml').glob('*'):
        with (OUT/f.name).open('xb') as stream:stream.write(f.read_bytes())
    print(json.dumps(dict(actualExit=code,observedTestExecutions=len(actual),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))));raise SystemExit(code)


if __name__=='__main__':main()
