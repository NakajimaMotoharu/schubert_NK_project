"""All original81 methods after Test-only lexical corrections; pure values/owned simple SDK, no actual DB/service."""
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

SOURCE='42ae92a74d57a9e1d031613d5b558af3ebe2925c'
NORMAL_SHA='77020a553a53f8c09d498899dbb3e5844121dc67023862901fa7ad82b12c1932'
PLAN_SHA='26c3c4fd22d61e6bd8dc26ddbf4c47baee7b98c3963352123a0fac1d80f88a09'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg13078-monitor-test-host-v1'
OUT=data.BASE/'PG13078-monitor-test-host-v1'


def main():
    invocation=capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    normal=data.read_checked(data.BASE/'PG13076-monitor-test-six-compile-v1/manifest.json',NORMAL_SHA)
    plan=data.read_checked(data.BASE/'PG13074-monitor-test-plan-v1/manifest.json',PLAN_SHA)
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    assert plan['actualExit']==0 and plan['totalCorrections']==11 and plan['originalTests']==81 and plan['newTests']==0 and plan['sameExecRequired'] and not plan['oldExecUnion']
    assert len(plan['eligibilityClosureSourceHashes'])==19
    hashes=normal['begin']['inputHashes']
    snapshot=Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==digest for p,digest in hashes.items())
    assert all(hashes[path]==digest for path,digest in plan['wholeTestSourceHashes'].items())
    assert all(hashes[path]==digest for path,digest in plan['eligibilityClosureSourceHashes'].items())
    helper=data.ROOT/'tools/quality/architecture/MonitorTestNamesJunitLauncher.java'
    helpertext=helper.read_text()
    assert 'EXPECTED_TESTS = 81;' in helpertext and 'EXPECTED_SUITES = 10;' in helpertext
    assert not any(word in helpertext for word in ['Class.forName','selectPackage(','scanClasspath'])
    cases=[]
    ordered_paths=list(dict.fromkeys(row['path'] for row in plan['cases']))
    assert set(ordered_paths)==set(plan['wholeTestSourceHashes'])
    reversed_map=dict(reversed(list(plan['wholeTestSourceHashes'].items())))
    assert [path for path in ordered_paths if path in reversed_map]==ordered_paths
    assert plan['cases']!=list(reversed(plan['cases'])) and len({(row['className'],row['method']) for row in plan['cases']})==81
    for path in ordered_paths:
        text=(snapshot/path).read_text()
        prohibited=['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','ProcessBuilder','System.getenv','System.setProperty','Class.forName','ServiceLoader','setAccessible','TemporaryInfrastructureException','WebStartupException']
        assert not any(word in text for word in prohibited)
        assert 'java.nio.file' not in text
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods)==len(set(methods))==({'AsyncQueueMonitorTest': 9, 'BackupHealthMonitorTest': 8, 'DlqHealthMonitorTest': 8, 'ExpiryBacklogMonitorTest': 8, 'IntegrityHealthMonitorTest': 8, 'RestartHealthMonitorTest': 8, 'TimedDbPoolMonitorTest': 8, 'TimedSyncLatencyMonitorTest': 8, 'TransferHealthMonitorTest': 8, 'WebLogBacklogMonitorTest': 8}[Path(path).stem])
        binary=path.split('/java/',1)[1][:-5].replace('/','.')
        assert all(binary+'#'+method in helpertext for method in methods)
        cases.extend(dict(className=binary,method=method,path=path,sourceSha256=hashes[path]) for method in methods)
    assert cases==plan['cases'] and len(cases)==81
    tc=data.ROOT.parent/'toolchain'
    modules=[snapshot/'src'/('schubert-nk-'+role) for role in ['batch']]
    libraries=[]
    for module in modules:
        libraries.extend((module/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep))
    libraries=list(dict.fromkeys(path for path in libraries if not path.endswith('-tests.jar')))
    jars={key:value['path'] for key,value in normal['jars'].items()}
    launcher=tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    assert data.sha(launcher.read_bytes())=='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    deps={str(path):data.sha(Path(path).read_bytes()) for path in [*jars.values(),*libraries,launcher,agent]}
    physical={str(path):data.sha(path.read_bytes()) for module in modules for path in (module/'target/test-classes').rglob('*.class')}
    entries=list(dict.fromkeys(map(str,[*[module/'target/test-classes' for module in modules],*jars.values(),*libraries,launcher])))
    unique={}
    for path in [*plan['eligibilityClosureSourceHashes'],*{row['path'] for row in cases},*plan['supportTestSourceHashes']]:
        binary=path.split('/java/',1)[1][:-5]+'.class';locations=[]
        for entry in entries:
            candidate=Path(entry)
            if candidate.is_dir():
                if (candidate/binary).is_file():
                    locations.append(entry)
            elif candidate.suffix=='.jar':
                with zipfile.ZipFile(candidate) as jar:
                    if binary in jar.namelist():
                        locations.append(entry)
        assert len(locations)==1
        unique[binary]=locations
    os.umask(0o077);SLOT.mkdir()
    cwd=SLOT/'test-cwd';cwd.mkdir()
    reader=SLOT/'launcher';reader.mkdir()
    cp=os.pathsep.join([str(reader),*entries])
    catalog=SLOT/'frozen-methods.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(row['className']+'\t'+row['method']+'\n' for row in cases))
    begin=dict(source=SOURCE,invocation=invocation,sourceInputHashes=hashes,normalManifestSha256=NORMAL_SHA,dependencyHashes=deps,physicalTestFiles=physical,helperPath=str(helper),helperSha256=data.sha(helper.read_bytes()),cases=cases,expectedMethods=81,expectedSuites=10,normalSnapshot=str(snapshot),testCwd=str(cwd),moduleJars=jars,classpath=cp,eligibilityClosureSourceHashes=plan['eligibilityClosureSourceHashes'],supportTestSourceHashes=plan['supportTestSourceHashes'],uniqueClassDefinitions=unique,judgement=plan['judgement'])
    data.write(SLOT/'begin.safe.json',begin);steps.SLOT=SLOT
    stages=[steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    session='PG13078-MONITORNAME-JP'
    command=[str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,'-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
    stages.append(steps.step('whole-monitor-test-names-jp',command,cwd,timeout=240))
    actual=[];xmls={}
    for path in sorted((SLOT/'xml').glob('TEST-*.xml')):
        node=ET.parse(path).getroot();xmls[path.name]=data.sha(path.read_bytes())
        actual.extend(dict(classname=row.get('classname'),name=row.get('name'),nonPass=[n.tag for n in row]) for row in node.findall('testcase'))
    passed=stages[-1]['actualExit']==0 and not stages[-1]['timedOut'] and len(xmls)==10 and len(actual)==81 and Counter((row['classname'],row['name']) for row in actual)==Counter((row['className'],row['method']) for row in cases) and not any(row['nonPass'] for row in actual)
    assert not list(cwd.iterdir()) and data.sha(helper.read_bytes())==begin['helperSha256']
    assert all(data.sha(Path(path).read_bytes())==digest for path,digest in {**deps,**physical}.items())
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in hashes.items())
    verify(invocation)
    value=dict(actualExit=0 if passed else stages[-1]['actualExit'] or 1,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,sessionId=session,observedTestExecutions=len(actual),execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()),classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()),oldExecUnion=False,coveragePendingIndependentPost=True,newAccepted=0,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value);OUT.mkdir();data.write(OUT/'manifest.json',value)
    for path in (SLOT/'xml').glob('*'):
        with (OUT/path.name).open('xb') as stream:
            stream.write(path.read_bytes())
    print(json.dumps(dict(actualExit=value['actualExit'],observedTestExecutions=len(actual),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(value['actualExit'])


if __name__=='__main__':
    main()
