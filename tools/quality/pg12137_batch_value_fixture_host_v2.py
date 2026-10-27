"""Original4 Batch pure enum and injected observation fixture methods; closed catalog, one fresh owned JVM and exec."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as steps

SOURCE = '8a229695c0ea503ebac8761993665242eeba0107'
NORMAL_SHA = '6894ef3e885fbe1d4995e5809fd82dc16fa88b0a3ccb02613c120370fdf56bb9'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg12137-batch-value-fixture-host-v2'
OUT = data.BASE/'PG12137-batch-value-fixture-host-v2'
FILES = ['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/EnumValueCatalogCompatibilityTest.java','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisDetailedValuesTest.java']


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG12134-batch-value-fixture-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,NORMAL_SHA)
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    inverse = data.read_checked(data.BASE/'PG12132-batch-value-fixture-source-post-v1/manifest.json',
        '8518f2bfae999441da38c66745979eba016b54906220cbbcffbdfeecec5407bf')
    assert inverse['actualExit'] == 0 and inverse['metadataNegativeVectors'] == 30
    hashes = normal['begin']['inputHashes']
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    eligibility_paths = ['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/mq/'+n+'.java' for n in ('ArtemisManagementReadinessClient','ArtemisQueuePressureClient','ArtemisStartupObservation')]+['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/'+n+'.java' for n in ('ApplicationUnit','MaintenanceUnit','RootStartupContext','InspectorUnitSnapshot','BackupUnitStartClient')]
    eligibility = {p:hashes[p] for p in eligibility_paths}
    assert all(data.sha((snapshot/p).read_bytes())==h for p,h in eligibility.items())
    # Only the explicitly reviewed nested enum getters/ownedBy and injected value methods are eligible.
    # These mixed source files also define real operations; no file-wide no-IO assertion is made.
    # The post must prove zero instructions in outer Root/Inspector/Backup and management query methods.
    helper = data.ROOT/'tools/quality/architecture/BatchValueFixtureJunitLauncher.java'
    helper_text = helper.read_text()
    cases = []
    for p in FILES:
        text = (snapshot/p).read_text()
        assert not any(word in text for word in ('@Before','@After','@ExtendWith','@Disabled','@TempDir','HttpServer.create(', 'new Socket(', 'openConnection(','ProcessBuilder','System.gc(','System.getenv','System.getProperty','getConnection(','setAccessible'))
        assert not re.search(r'\bstatic\s*\{',text)
        assert not any(word in text for word in ('ActiveMQClient','EmbeddedActiveMQ','System.getProperty','newInputStream','createSession(','.start()','RootStartupContext.create(','BackupUnitStartClient.create(','InspectorUnitSnapshot.parse('))
        if Path(p).stem=='EnumValueCatalogCompatibilityTest':
            assert 'ObjectStreamClass.lookup(type)' in text and 'new ObjectInputStream' not in text
        else:
            assert 'borrowed session not needed by fixed reader fixture' in text and 'new ArtemisStartupObservation(' not in text
            assert text.count('new ArtemisManagementReadinessClient(')==text.count('new ArtemisQueuePressureClient(')==1
        assert text.count('Runtime.getRuntime()') == text.count('Runtime.getRuntime().availableProcessors()')
        methods = re.findall(r'@Test\s+void (\w+)\(\)',text)
        assert len(methods) == len(set(methods)) == {'EnumValueCatalogCompatibilityTest':1,'ArtemisDetailedValuesTest':3}[Path(p).stem]
        for method in methods:
            binary = re.search(r'package ([\w.]+);',text)[1]+'.'+Path(p).stem
            assert binary+'#'+method in helper_text
            cases.append(dict(className=binary,method=method,path=p,sourceSha256=hashes[p]))
    assert 'EXPECTED_TESTS = 4;' in helper_text and 'EXPECTED_SUITES = 2;' in helper_text
    assert not any(x in helper_text for x in ('Class.forName','selectPackage(', 'scanClasspath'))
    tc = data.ROOT.parent/'toolchain'
    modules = [snapshot/('src/schubert-nk-'+role) for role in ('batch',)]
    libraries = list(dict.fromkeys(p for cwd in modules for p in (cwd/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep)))
    jars = {k:v['path'] for k,v in normal['jars'].items()}
    test_directories = [cwd/'target/test-classes' for cwd in modules]
    physical = {str(p):data.sha(p.read_bytes()) for directory in test_directories for p in directory.rglob('*.class')}
    bootstrap_tests = snapshot/'src/schubert-nk-bootstrap/target/schubert-nk-bootstrap-0.1.0-SNAPSHOT-tests.jar'
    assert all(Path(p).is_file() and not Path(p).is_symlink() and
        (p.startswith(str(tc/'m2/repository')+'/') or p in jars.values() or Path(p) == bootstrap_tests) for p in libraries)
    launcher = tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    assert data.sha(launcher.read_bytes()) == '0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    agent = tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    deps = {str(p):data.sha(Path(p).read_bytes()) for p in [*jars.values(),*libraries,launcher,agent]}
    helper_hash = data.sha(helper.read_bytes())
    os.umask(0o077)
    SLOT.mkdir()
    test_cwd = SLOT/'test-cwd'
    test_cwd.mkdir()
    assert not list(test_cwd.iterdir()) and not test_cwd.is_symlink()
    reader = SLOT/'launcher'
    reader.mkdir()
    catalog = SLOT/'frozen-methods.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(r['className']+'\t'+r['method']+'\n' for r in cases))
    cp_entries = list(dict.fromkeys(map(str,[reader,*test_directories,*jars.values(),*libraries,launcher])))
    assert jars['batch'] in cp_entries and all(p in cp_entries for p in jars.values())
    targets=['dev/codex/schubert/nk/batch/platform/ApplicationUnit.class','dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient.class']
    definitions={}
    for target in targets:
        locations=[]
        for entry in cp_entries:
            path=Path(entry)
            if path.is_dir():
                if (path/target).is_file():locations.append(entry)
            elif path.suffix=='.jar':
                with __import__('zipfile').ZipFile(path) as jar:
                    if target in jar.namelist():locations.append(entry)
        assert locations==[jars['batch']]
        definitions[target]=locations
    cp = os.pathsep.join(cp_entries)
    begin = dict(source=SOURCE,normalManifestSha256=data.sha(normal_path.read_bytes()),invocation=invocation,
        sourceInputHashes=hashes,eligibilityClosureSourceHashes=eligibility,physicalTestFiles=physical,dependencyHashes=deps,helperSha256=helper_hash,
        helperPath=str(helper),cases=cases,expectedMethods=4,expectedSuites=2,normalSnapshot=str(snapshot),
        judgement='PT_DEFAULT_ENUM_VALUES_ONLY_AND_INJECTED_READER_MAPS_UNUSED_SESSION_PROXY_NO_BROKER_UNIT_ROOT_OPERATIONS',
        targetNetworkPermitted=False,targetDatabasePermitted=False,targetVmRootServicePermitted=False,
        classpath=cp,requiredClassDefinitions=definitions,testCwd=str(test_cwd),moduleJars=jars,heldTestExtraction=False)
    data.write(SLOT/'begin.safe.json',begin)
    steps.SLOT = SLOT
    stages = [steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    code = stages[0]['actualExit']
    actual,xmls = [],{}
    session = 'PG12136-BATCHVALUE-JP'
    if code == 0 and not stages[0]['timedOut']:
        command = [str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP',
            '-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,
            '-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('api-web-scrape-fixture-jp',command,test_cwd,timeout=240))
        for file in sorted((SLOT/'xml').glob('TEST-*.xml')):
            root = ET.parse(file).getroot()
            xmls[file.name] = data.sha(file.read_bytes())
            actual += [dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in root.findall('testcase')]
        passed = (stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut'] and len(xmls) == 2 and len(actual) == 4
            and Counter((r['classname'],r['name']) for r in actual) == Counter((r['className'],r['method']) for r in cases)
            and not any(r['nonPass'] for r in actual))
        code = 0 if passed else stages[-1]['actualExit'] or 1
    else:
        code = code or 1
    assert not list(test_cwd.iterdir())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**physical}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    assert data.sha(helper.read_bytes()) == helper_hash
    verify(invocation)
    value = dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,
        sessionId=session,observedTestExecutions=len(actual),execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,
        classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()) if (SLOT/'classload-metadata.log').exists() else None,
        oldExecUnion=False,coveragePendingIndependentPost=True,whole451Accepted=False,newAccepted=0,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',value)
    OUT.mkdir()
    data.write(OUT/'manifest.json',value)
    for file in (SLOT/'xml').glob('*'):
        with (OUT/file.name).open('xb') as stream:
            stream.write(file.read_bytes())
    print(json.dumps(dict(actualExit=code,observedTestExecutions=len(actual),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
