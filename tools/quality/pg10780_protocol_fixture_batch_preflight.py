"""Concrete Protocol-only full-method catalog: memory values, bounded streams and fixed resources."""
import json
import os
from pathlib import Path
import re
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '5cc74a2e437d19b22b07eb9a57c8d04414109e9b'
OUT = data.BASE/'PG10780-protocol-fixture-batch-preflight-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10778-protocol-fixture-batch-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    proof = data.read_checked(data.BASE/'PG10774-protocol-duplicate-batch-source-post-v1/manifest.json',
        'b2e54df0e380e0afbd37e2bcfeba1cd752940ccf1d869cef60c322ef5271f5f4')
    assert proof['actualExit'] == 0 and proof['constantsAdded'] == 59 and proof['metadataNegativeVectors'] == 33
    files = sorted(p for p in hashes if p.startswith('src/schubert-nk-protocol/src/test/java/') and p.endswith('.java'))
    assert len(files) == 23
    cases,reviewed = [],[]
    for path in files:
        text = (snapshot/path).read_text()
        assert not any(marker in text for marker in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir','@TestFactory','@ParameterizedTest'))
        assert not re.search(r'\bstatic\s*\{',text)
        imports = re.findall(r'^import (.*);',text,re.M)
        assert all(i.startswith(('java.','dev.codex.schubert.nk.protocol.','org.junit.jupiter.api.Test','static org.junit.jupiter.api.Assertions.')) for i in imports)
        assert not any(word in text for word in ('java.net.','java.nio.file.','ProcessBuilder','Runtime.getRuntime','System.exit','System.getenv','System.getProperty','setAccessible','org.postgresql','org.apache.activemq','getConnection('))
        package = re.search(r'package ([a-zA-Z0-9_.]+);',text)[1]
        methods = re.findall(r'@Test\s+void (\w+)\(\s*\)',text)
        binary = package+'.'+Path(path).stem
        for method in methods:
            cases.append(dict(className=binary,method=method,testId='PT-PRO-FIX-'+str(len(cases)+1).zfill(3),
                path=path,sourceSha256=hashes[path],changeOwner='WBS-F03',canonicalOwnerNotInferred=True))
        reviewed.append(dict(path=path,sha256=hashes[path],methods=len(methods),imports=imports,
            sideEffectDomain='PURE_PROTOCOL_VALUES_FIXED_CLASSPATH_FIXTURES_MEMORY_STREAMS_BOUNDED_LOCAL_THREADS'))
    assert len(cases) == 102 and len({r['className'] for r in cases}) == 22
    tc = data.ROOT.parent/'toolchain'
    directory = snapshot/'src/schubert-nk-protocol/target/test-classes'
    physical = {str(p):data.sha(p.read_bytes()) for p in sorted(directory.rglob('*.class'))}
    assert len(physical) >= 23
    libraries = (snapshot/'src/schubert-nk-protocol/target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep)
    allowed = tuple(str(tc/'m2/repository'/group)+'/' for group in ('org/jspecify','org/junit','org/opentest4j','org/apiguardian'))
    assert libraries and all(p.startswith(allowed) and Path(p).is_file() and not Path(p).is_symlink() for p in libraries)
    launcher = tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    assert data.sha(launcher.read_bytes()) == '0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    agent = tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    protocol = Path(normal['jars']['protocol']['path'])
    dependencies = {str(p):data.sha(Path(p).read_bytes()) for p in [protocol,*libraries,launcher,agent]}
    main_classes = {}
    with zipfile.ZipFile(protocol) as jar:
        for name in jar.namelist():
            if name.endswith('.class'):
                assert name.startswith('dev/codex/schubert/nk/protocol/') and '..' not in Path(name).parts
                main_classes[name] = data.sha(jar.read(name))
    assert len(main_classes) == 176
    helper = data.ROOT/'tools/quality/architecture/ProtocolFixtureBatchJunitLauncher.java'
    helper_text = helper.read_text()
    assert all(r['className']+'#'+r['method'] in helper_text for r in cases)
    assert 'EXPECTED_TESTS = 102;' in helper_text and 'EXPECTED_SUITES = 22;' in helper_text
    assert 'junit.jupiter.extensions.autodetection.enabled' in helper_text
    assert not any(word in helper_text for word in ('Class.forName','selectPackage(', 'scanClasspath','WebStartupGraph','ApiStartupGraph'))
    resources = {p:h for p,h in hashes.items() if p.startswith('src/schubert-nk-protocol/src/test/resources/')}
    assert resources
    spec = data.ROOT/'evidence/01_PT/001_NK-PRO-001/1189_Protocol残重複fixture一括PGPT仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        expectedTestsPerLocale=102,expectedSuitesPerLocale=22,locales=['ja-JP'],expectedUniqueMethods=102,
        normalSnapshot=str(snapshot),allCurrentSourceInputHashes=hashes,physicalTestFiles=physical,
        completeProtocolMainClasses=main_classes,dependencyHashes=dependencies,libraryClasspath=libraries,
        launcherJar=str(launcher),jacocoAgent=str(agent),protocolJar=str(protocol),testClassesDirectory=str(directory),
        helperPath=str(helper),helperSha256=data.sha(helper.read_bytes()),specPath=str(spec.relative_to(data.ROOT)),specSha256=data.sha(spec.read_bytes()),
        reviewedSources=reviewed,fixedClasspathResources=resources,
        concreteReview=dict(reflection='public Protocol constructors/getters only; fixed fields/named-accessors TSV; no access override',
            serialization='fixed manually assembled AnswerState enum bytes only, ByteArrayInputStream; no external input',
            concurrency='PayloadGoldenVectorTest:8own executor tasks/CountDownLatch; try-with-resources; outer own timeout',
            streams='ByteArray and own finite Chunked/Zero/Counting streams; largest48MB decoded fixture; no actual file handle',
            classpath='only Protocol jar/test classes plus JUnit/jspecify; no backend runtime',
            purpose='needed module regression after11Test fixture edits and complete current artifact counters; not replay for confirmation'),
        judgement='PT_DEFAULT_CONCRETE_PROTOCOL_ONLY_MODULE_REGRESSION',actualNetworkPermitted=False,actualDatabasePermitted=False,
        actualVmRootServicePermitted=False,heldTestExtraction=False,newTestFixtureHarnessForHeldOperations=False,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
