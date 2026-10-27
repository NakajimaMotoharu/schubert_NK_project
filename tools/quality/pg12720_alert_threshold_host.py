"""Original whole14 pure alert thresholds fixture, fixed memory/owned workers, no collector I/O."""
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

SOURCE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
NORMAL_SHA='5433fb79732be52686b99e8ec665a0ebb02752a90004cc777eedb3b4d31ba1c7'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12720-alert-threshold-host-v1'
OUT=data.BASE/'PG12720-alert-threshold-host-v1'
MAIN='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/'
TEST=MAIN.replace('/main/','/test/')+'AlertThresholdsTest.java'


def main():
    invocation=capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    normal=data.read_checked(data.BASE/'PG12718-alert-threshold-six-compile-v1/manifest.json',NORMAL_SHA)
    plan=data.read_checked(data.BASE/'PG12716-alert-threshold-plan-v1/manifest.json','9f59c8646f08f5df99f88b599219640d5b4aa531b3e4c8dabeb733f5ae414500')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    assert plan['actualExit']==0 and plan['totalCorrections']==2 and plan['originalTests']==14 and plan['metadataNegativeVectors']==9
    hashes=normal['begin']['inputHashes']
    snapshot=Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==digest for p,digest in hashes.items())
    closure={p:hashes[p] for p in [MAIN+'AlertThresholds.java',MAIN+'AlertLifecycle.java']}
    helper=data.ROOT/'tools/quality/architecture/AlertThresholdJunitLauncher.java'
    text=(snapshot/TEST).read_text()
    assert not any(value in text for value in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.nio.file','java.net.','java.sql.','ProcessBuilder','System.getenv','System.getProperty','Class.forName','ServiceLoader','setAccessible'])
    methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
    assert len(methods)==len(set(methods))==14
    helpertext=helper.read_text()
    assert 'EXPECTED_TESTS = 14;' in helpertext and 'EXPECTED_SUITES = 1;' in helpertext
    assert not any(value in helpertext for value in ['Class.forName','selectPackage(','scanClasspath'])
    cases=[dict(className='dev.codex.schubert.nk.batch.monitoring.AlertThresholdsTest',method=method,path=TEST,sourceSha256=hashes[TEST]) for method in methods]
    assert all(row['className']+'#'+row['method'] in helpertext for row in cases)
    tc=data.ROOT.parent/'toolchain'
    module=snapshot/'src/schubert-nk-batch'
    libraries=list(dict.fromkeys((module/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep)))
    libraries=[p for p in libraries if not p.endswith('-tests.jar')]
    jars={k:v['path'] for k,v in normal['jars'].items()}
    launcher=tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    assert data.sha(launcher.read_bytes())=='0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    deps={str(p):data.sha(Path(p).read_bytes()) for p in [*jars.values(),*libraries,launcher,agent]}
    physical={str(p):data.sha(p.read_bytes()) for p in (module/'target/test-classes').rglob('*.class')}
    # Unique exact class definitions, no package/classpath discovery.
    entries=list(dict.fromkeys(map(str,[module/'target/test-classes',*jars.values(),*libraries,launcher])))
    unique={}
    for binary in ['dev/codex/schubert/nk/batch/monitoring/'+name+'.class' for name in ['AlertThresholds','AlertLifecycle','AlertLifecycle$Severity','AlertThresholdsTest']]:
        locations=[]
        for entry in entries:
            path=Path(entry)
            if path.is_dir():
                if (path/binary).is_file():
                    locations.append(entry)
            elif path.suffix=='.jar':
                with zipfile.ZipFile(path) as jar:
                    if binary in jar.namelist():
                        locations.append(entry)
        assert len(locations)==1
        unique[binary]=locations
    os.umask(0o077)
    SLOT.mkdir()
    cwd=SLOT/'test-cwd';cwd.mkdir()
    reader=SLOT/'launcher';reader.mkdir()
    cp=os.pathsep.join([str(reader),*entries])
    catalog=SLOT/'frozen-methods.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(r['className']+'\t'+r['method']+'\n' for r in cases))
    begin=dict(source=SOURCE,invocation=invocation,sourceInputHashes=hashes,normalManifestSha256=NORMAL_SHA,dependencyHashes=deps,physicalTestFiles=physical,helperPath=str(helper),helperSha256=data.sha(helper.read_bytes()),cases=cases,expectedMethods=14,expectedSuites=1,normalSnapshot=str(snapshot),testCwd=str(cwd),moduleJars=jars,classpath=cp,eligibilityClosureSourceHashes=closure,uniqueClassDefinitions=unique,judgement='PT_DEFAULT_PURE_THRESHOLD_MEMORY_OWN_FOUR_WORKER_64_CALLBACK_NO_COLLECTOR_OR_IO')
    data.write(SLOT/'begin.safe.json',begin)
    steps.SLOT=SLOT
    stages=[steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    session='PG12720-ALERTTHRESH-JP'
    command=[str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,'-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
    stages.append(steps.step('pure-alert-threshold-jp',command,cwd,timeout=240))
    actual=[];xmls={}
    for path in sorted((SLOT/'xml').glob('TEST-*.xml')):
        node=ET.parse(path).getroot()
        xmls[path.name]=data.sha(path.read_bytes())
        actual.extend(dict(classname=row.get('classname'),name=row.get('name'),nonPass=[n.tag for n in row]) for row in node.findall('testcase'))
    passed=stages[-1]['actualExit']==0 and not stages[-1]['timedOut'] and len(xmls)==1 and len(actual)==14 and Counter((r['classname'],r['name']) for r in actual)==Counter((r['className'],r['method']) for r in cases) and not any(r['nonPass'] for r in actual)
    assert not list(cwd.iterdir())
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**deps,**physical}.items())
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in hashes.items())
    assert data.sha(helper.read_bytes())==begin['helperSha256']
    verify(invocation)
    value=dict(actualExit=0 if passed else stages[-1]['actualExit'] or 1,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,sessionId=session,observedTestExecutions=len(actual),execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()),classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()),oldExecUnion=False,coveragePendingIndependentPost=True,newAccepted=0,whole451Accepted=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir();data.write(OUT/'manifest.json',value)
    for path in (SLOT/'xml').glob('*'):
        with (OUT/path.name).open('xb') as stream:
            stream.write(path.read_bytes())
    print(json.dumps(dict(actualExit=value['actualExit'],observedTestExecutions=len(actual),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(value['actualExit'])


if __name__ == '__main__':
    main()
