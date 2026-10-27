"""Original thirty-four supplied scalar metric tests; closed in-memory SDK catalog only."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as steps

SOURCE = '5eeb36dd1995ebbca2eb3ba7be30b4c4e1b69b81'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg11186-api-catalog-scalar-pool-host-v1'
OUT = data.BASE/'PG11186-api-catalog-scalar-pool-host-v1'
FILES = ['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/'+p+'Test.java' for p in ('ApiMetricCatalog','ApiScalarMetricExporter','DbPoolMetricRecorder')]


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG11184-api-catalog-scalar-pool-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    inverse = data.read_checked(data.BASE/'PG11182-api-catalog-scalar-pool-source-post-v1/manifest.json',
        'c49c95c433cbd6ea2cb1ae67e45341b3de9483dcf63d75b3a4ac525421c42e0c')
    assert inverse['actualExit'] == 0 and inverse['metadataNegativeVectors'] == 9
    hashes = normal['begin']['inputHashes']
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    helper = data.ROOT/'tools/quality/architecture/CatalogScalarPoolFixtureJunitLauncher.java'
    helper_text = helper.read_text()
    cases = []
    for p in FILES:
        text = (snapshot/p).read_text()
        assert not any(word in text for word in ('@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','ProcessBuilder','Runtime.getRuntime','System.getenv','System.getProperty','getConnection(','setAccessible'))
        assert not re.search(r'\bstatic\s*\{',text)
        methods = re.findall(r'@Test\s+void (\w+)\(\)',text)
        assert len(methods) == len(set(methods)) == dict(ApiMetricCatalogTest=14,ApiScalarMetricExporterTest=24,DbPoolMetricRecorderTest=8)[Path(p).stem]
        for method in methods:
            binary = re.search(r'package ([\w.]+);',text)[1]+'.'+Path(p).stem
            assert binary+'#'+method in helper_text
            cases.append(dict(className=binary,method=method,path=p,sourceSha256=hashes[p]))
    assert 'EXPECTED_TESTS = 46;' in helper_text and 'EXPECTED_SUITES = 3;' in helper_text
    assert not any(x in helper_text for x in ('Class.forName','selectPackage(', 'scanClasspath'))
    tc = data.ROOT.parent/'toolchain'
    cwd = snapshot/'src/schubert-nk-api'
    libraries = (cwd/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep)
    jars = {k:v['path'] for k,v in normal['jars'].items()}
    test_directory = cwd/'target/test-classes'
    physical = {str(p):data.sha(p.read_bytes()) for p in test_directory.rglob('*.class')}
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
    cp = os.pathsep.join(map(str,[reader,test_directory,jars['api'],*libraries,launcher]))
    begin = dict(source=SOURCE,normalManifestSha256=data.sha(normal_path.read_bytes()),invocation=invocation,
        sourceInputHashes=hashes,physicalTestFiles=physical,dependencyHashes=deps,helperSha256=helper_hash,
        helperPath=str(helper),cases=cases,expectedMethods=46,expectedSuites=3,normalSnapshot=str(snapshot),
        judgement='PT_DEFAULT_NOOP_METER_MEMORY_WRITER_FIXED_LABELS_SUPPLIED_POOL_OWN_SDK_NO_SQL_JMS_HTTP',
        targetNetworkPermitted=False,targetDatabasePermitted=False,targetVmRootServicePermitted=False,
        classpath=cp,testCwd=str(test_cwd),moduleJars=jars,heldTestExtraction=False)
    data.write(SLOT/'begin.safe.json',begin)
    steps.SLOT = SLOT
    stages = [steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    code = stages[0]['actualExit']
    actual,xmls = [],{}
    session = 'PG11186-APIREQ-JP'
    if code == 0 and not stages[0]['timedOut']:
        command = [str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP',
            '-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,
            '-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('api-catalog-scalar-pool-jp',command,test_cwd,timeout=240))
        for file in sorted((SLOT/'xml').glob('TEST-*.xml')):
            root = ET.parse(file).getroot()
            xmls[file.name] = data.sha(file.read_bytes())
            actual += [dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in root.findall('testcase')]
        passed = (stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut'] and len(xmls) == 3 and len(actual) == 46
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


