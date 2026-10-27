"""Original18 whole API value methods; one fresh owned JVM/exec."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as steps
from frozen_selected_scope import derive_facts,require_classpath

SOURCE = '7368ba9d4a38677f5eade903771832e612aa42b5'
NORMAL_SHA = '776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg12288-api-value-host-v1'
OUT = data.BASE/'PG12288-api-value-host-v1'
FILES = [r['path'] for r in data.read_checked(data.BASE/'PG12285-api-value-plan-v3/manifest.json','350e7513bbd53a67ff76ec960a6e4a17e9360c129a1d5c2149f56a968ff43823')['sourceChanges']]
COUNTS=dict(StubAnswerProviderTest=5,PasswordPolicyTest=3,OutboxDlqMetadataTest=2,GeneratedMetricValueContractTest=8)
TRACE='provider=STUB\nanswerLength=0\nclockReadsPerCall=1\nconcurrentCalls=64\nuniqueClockValues=64\nexternalCalls=0\nrawBodySaved=false\n'



def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG12286-api-value-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,NORMAL_SHA)
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    inverse = data.read_checked(data.BASE/'PG12284-api-value-source-post-v1/manifest.json',
        'e99f268993a69db56a11e4c56f1292fc8051af028e263d9ddff879f1bacb8194')
    assert inverse['actualExit'] == 0 and inverse['metadataNegativeVectors'] == 30
    hashes = normal['begin']['inputHashes']
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    plan=data.read_checked(data.BASE/'PG12285-api-value-plan-v3/manifest.json','350e7513bbd53a67ff76ec960a6e4a17e9360c129a1d5c2149f56a968ff43823')
    facts=derive_facts(plan,normal,SOURCE);assert set(facts['sources'])==set(FILES) and facts['modules']==['api']
    eligibility_paths=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'+p+'.java' for p in ['application/question/AnswerProvider', 'application/question/AnswerResult', 'application/question/StubAnswerProvider', 'security/PasswordPolicy', 'messaging/outbound/OutboxDlqMetadata', 'messaging/outbound/OutboxDestination', 'messaging/outbound/OutboxRequest', 'messaging/outbound/OutboxEntry', 'monitoring/DbPoolMetricRecorder', 'monitoring/OutboxRowsMetricRecorder', 'monitoring/AsyncJobMetricRecorder', 'monitoring/OperationMismatchMetricRecorder']]
    eligibility={p:hashes[p] for p in eligibility_paths}
    for p in eligibility:
        t=(snapshot/p).read_text();assert data.sha(t.encode())==hashes[p]
        assert not any(w in t for w in ('TemporaryInfrastructureException','WebStartupException','Class.forName','java.sql.','java.nio.file.','java.net.','ProcessBuilder','JMSContext','ConnectionFactory','getByName(','.connect(','.openConnection('))
    helper = data.ROOT/'tools/quality/architecture/ApiValueFixtureJunitLauncher.java'
    helper_text = helper.read_text()
    cases = []
    for p in FILES:
        text = (snapshot/p).read_text()
        assert not any(word in text for word in ('@Before','@After','@ExtendWith','@Disabled','@TempDir','HttpServer.create(', 'new Socket(', 'openConnection(','ProcessBuilder','System.gc(','System.getenv','System.getProperty','getConnection(','setAccessible'))
        assert not re.search(r'\bstatic\s*\{',text)
        assert not any(word in text for word in ('ActiveMQClient','EmbeddedActiveMQ','newInputStream','createSession(','.start()','java.sql.','getByName('))
        if Path(p).stem=='StubAnswerProviderTest':
            assert 'executor.invokeAll(tasks, 5, TimeUnit.SECONDS)' in text
            assert 'Path.of("target/question-stub-traces")' in text
            assert text.count('Files.createDirectories(')==text.count('Files.writeString(')==1
        else:
            assert not any(w in text for w in ('Files.','Path.of(', 'new StubAnswerProvider','Executors.'))
        assert text.count('Runtime.getRuntime()') == text.count('Runtime.getRuntime().availableProcessors()')
        methods = re.findall(r'@Test\s+(?:@DisplayName\([^\n]*\)\s+)?void (\w+)\(\)',text)
        assert len(methods) == len(set(methods)) == COUNTS[Path(p).stem]
        for method in methods:
            binary = re.search(r'package ([\w.]+);',text)[1]+'.'+Path(p).stem
            assert binary+'#'+method in helper_text
            cases.append(dict(className=binary,method=method,path=p,sourceSha256=hashes[p]))
    assert 'EXPECTED_TESTS = 18;' in helper_text and 'EXPECTED_SUITES = 4;' in helper_text
    assert not any(x in helper_text for x in ('Class.forName','selectPackage(', 'scanClasspath'))
    tc = data.ROOT.parent/'toolchain'
    modules = [snapshot/('src/schubert-nk-'+role) for role in facts['modules']]
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
    cp_entries = list(require_classpath(facts,list(dict.fromkeys(map(str,[reader,*test_directories,*jars.values(),*libraries,launcher])))))
    assert jars['web'] in cp_entries and all(p in cp_entries for p in jars.values())
    targets={p.split('/java/',1)[1][:-5]+'.class':'api' for p in eligibility_paths}
    definitions={}
    for target,role in targets.items():
        locations=[]
        for entry in cp_entries:
            path=Path(entry)
            if path.is_dir():
                if (path/target).is_file():locations.append(entry)
            elif path.suffix=='.jar':
                with __import__('zipfile').ZipFile(path) as jar:
                    if target in jar.namelist():locations.append(entry)
        assert locations==[jars[role]];definitions[target]=locations
    cp = os.pathsep.join(cp_entries)
    begin = dict(source=SOURCE,normalManifestSha256=data.sha(normal_path.read_bytes()),invocation=invocation,
        sourceInputHashes=hashes,eligibilityClosureSourceHashes=eligibility,physicalTestFiles=physical,dependencyHashes=deps,helperSha256=helper_hash,
        helperPath=str(helper),cases=cases,expectedMethods=18,expectedSuites=4,normalSnapshot=str(snapshot),
        judgement='PT_DEFAULT_SYNTHETIC_CLOCK_UNICODE_PASSWORD_DLQ_VALUES_RECORD_ENUM_NO_EXTERNAL_CONNECTION_OWNED_PUBLIC_TRACE_ONLY',
        targetNetworkPermitted=False,targetDatabasePermitted=False,targetVmRootServicePermitted=False,
        classpath=cp,requiredClassDefinitions=definitions,testCwd=str(test_cwd),moduleJars=jars,heldTestExtraction=False)
    data.write(SLOT/'begin.safe.json',begin)
    steps.SLOT = SLOT
    stages = [steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    code = stages[0]['actualExit']
    actual,xmls = [],{}
    session = 'PG12288-APIVALUE-JP'
    if code == 0 and not stages[0]['timedOut']:
        command = [str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP',
            '-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid='+session,
            '-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',cp,helper.stem,str(SLOT/'xml'),str(catalog),'ja-JP']
        stages.append(steps.step('api-web-scrape-fixture-jp',command,test_cwd,timeout=240))
        for file in sorted((SLOT/'xml').glob('TEST-*.xml')):
            root = ET.parse(file).getroot()
            xmls[file.name] = data.sha(file.read_bytes())
            actual += [dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in root.findall('testcase')]
        passed = (stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut'] and len(xmls) == 4 and len(actual) == 18
            and Counter((r['classname'],r['name']) for r in actual) == Counter((r['className'],r['method']) for r in cases)
            and not any(r['nonPass'] for r in actual))
        code = 0 if passed else stages[-1]['actualExit'] or 1
    else:
        code = code or 1
    written={p.relative_to(test_cwd).as_posix():p for p in test_cwd.rglob('*') if p.is_file()}
    assert set(written)=={'target/question-stub-traces/PT-ASY-STB005.txt'}
    assert all(not p.is_symlink() for p in test_cwd.rglob('*'))
    assert next(iter(written.values())).read_text()==TRACE
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**physical}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    assert data.sha(helper.read_bytes()) == helper_hash
    verify(invocation)
    value = dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,
        sessionId=session,publicFixtureFileHashes={p:data.sha(f.read_bytes()) for p,f in written.items()},observedTestExecutions=len(actual),execSha256=data.sha((SLOT/'jacoco.exec').read_bytes()) if (SLOT/'jacoco.exec').exists() else None,
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
