"""Original7 JSON codec cases plus5 necessary unchanged v2 contracts; closed catalog, one fresh owned JVM and exec."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as steps

SOURCE = '264dc69591876147d76c19082cb69658cfe03dd8'
NORMAL_SHA = '3cc0fa3b71e348b8d5821b1269e616a69999c0c5467d6f7bb38c9b3cf69830e0'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg11896-session-json-fixture-host-v1'
OUT = data.BASE/'PG11896-session-json-fixture-host-v1'
FILES = [f'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/{name}.java' for name in ('SessionAttributeCodecTest','SessionOperationTokenV2Test')]


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG11894-session-json-fixture-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,NORMAL_SHA)
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    inverse = data.read_checked(data.BASE/'PG11893-session-json-fixture-source-post-v2/manifest.json',
        'f6389c679e97b98ccd410e0c19b03b875ec852c6d4586bab3e80f1fec500dac7')
    assert inverse['actualExit'] == 0 and inverse['metadataNegativeVectors'] == 20
    hashes = normal['begin']['inputHashes']
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert len(inverse['sourceChanges']) == 1 and all(r['sha256'] == hashes[r['path']] for r in inverse['sourceChanges'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    eligibility_paths = [f'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/{name}.java' for name in ('session/SessionAttributeCodec','session/SessionAttributes','session/SessionPrincipal','session/SessionOperationToken','session/SessionAttributeException','security/SavedRequestTarget')]+[f'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/{name}.java' for name in ('header/AuthenticationContext','layout/semantic/UserRole','layout/semantic/WireEnum')]+[FILES[-1]]
    eligibility = {}
    for path in eligibility_paths:
        text = (snapshot/path).read_text();assert data.sha(text.encode()) == hashes[path]
        assert not any(word in text for word in ('TemporaryInfrastructureException','WebStartupException','DriverManager','getConnection(','Class.forName','new Socket(','ProcessBuilder','@Before','@After','@ExtendWith'))
        assert not re.search(r'\bstatic\s*\{',text)
        eligibility[path] = hashes[path]
    helper = data.ROOT/'tools/quality/architecture/SessionJsonFixtureJunitLauncher.java'
    helper_text = helper.read_text()
    cases = []
    for p in FILES:
        text = (snapshot/p).read_text()
        assert not any(word in text for word in ('@Before','@After','@ExtendWith','@Disabled','@TempDir','HttpServer.create(', 'new Socket(', 'openConnection(','ProcessBuilder','System.gc(','System.getenv','System.getProperty','getConnection(','setAccessible'))
        assert not re.search(r'\bstatic\s*\{',text)
        assert text.count('Runtime.getRuntime()') == text.count('Runtime.getRuntime().availableProcessors()')
        methods = re.findall(r'@Test\s+void (\w+)\(\)',text)
        assert len(methods) == len(set(methods)) == {'SessionAttributeCodecTest':7,'SessionOperationTokenV2Test':5}[Path(p).stem]
        for method in methods:
            binary = re.search(r'package ([\w.]+);',text)[1]+'.'+Path(p).stem
            assert binary+'#'+method in helper_text
            cases.append(dict(className=binary,method=method,path=p,sourceSha256=hashes[p]))
    assert 'EXPECTED_TESTS = 12;' in helper_text and 'EXPECTED_SUITES = 2;' in helper_text
    assert not any(x in helper_text for x in ('Class.forName','selectPackage(', 'scanClasspath'))
    tc = data.ROOT.parent/'toolchain'
    modules = [snapshot/('src/schubert-nk-'+role) for role in ('web',)]
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
    cp = os.pathsep.join(map(str,[reader,*test_directories,jars['api'],jars['web'],jars['protocol'],*libraries,launcher]))
    begin = dict(source=SOURCE,normalManifestSha256=data.sha(normal_path.read_bytes()),invocation=invocation,
        sourceInputHashes=hashes,eligibilityClosureSourceHashes=eligibility,physicalTestFiles=physical,dependencyHashes=deps,helperSha256=helper_hash,
        helperPath=str(helper),cases=cases,expectedMethods=12,expectedSuites=2,normalSnapshot=str(snapshot),
        judgement='PT_DEFAULT_STRICT_JSON_VALUE_URI_SYNTAX_FINITE_OWN_THREADS_NO_AUTH_KEY_DB_SOCKET_ROOT',
        targetNetworkPermitted=False,targetDatabasePermitted=False,targetVmRootServicePermitted=False,
        classpath=cp,testCwd=str(test_cwd),moduleJars=jars,heldTestExtraction=False)
    data.write(SLOT/'begin.safe.json',begin)
    steps.SLOT = SLOT
    stages = [steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    code = stages[0]['actualExit']
    actual,xmls = [],{}
    session = 'PG11896-SESSIONJSON-JP'
    if code == 0 and not stages[0]['timedOut']:
        command = [str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP',
            '-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,
            '-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('session-json-fixture-jp',command,test_cwd,timeout=240))
        for file in sorted((SLOT/'xml').glob('TEST-*.xml')):
            root = ET.parse(file).getroot()
            xmls[file.name] = data.sha(file.read_bytes())
            actual += [dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in root.findall('testcase')]
        passed = (stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut'] and len(xmls) == 2 and len(actual) == 12
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


