"""Closed four-method pure Protocol semantic catalog and independent primitive expectations; no target execution."""
from pathlib import Path
import json
import os
import re
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '1f20074cdfd20e13527525ed8d0e57faff28e276'
OUT = data.BASE/'PG10758-protocol-semantic-preflight-v1'
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/SemanticFieldValueTest.java'
METHODS = ('semanticHelpersDecodeAndEncodeEverySupportedShape',
    'semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects',
    'semanticValueObjectsNormalizeValidateCompareAndRedact','semanticEncodingHelpersRejectNullReferences')
BINARY = 'dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10756-protocol-semantic-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    plan = data.read_checked(data.BASE/'PG10752-protocol-semantic-oracle-plan-v1/manifest.json',
        '2f6772ed719306ad5fac724b5aa1bf0e3037e724d056c41f1be34e81a557f99c')
    assert plan['sourceChanges'][0]['path'] == TEST and plan['sourceChanges'][0]['sha256'] == hashes[TEST]
    text = (snapshot/TEST).read_text()
    assert not any(marker in text for marker in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir'))
    assert not re.search(r'\bstatic\s*\{',text)
    available = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
    assert len(available) == 4 and set(METHODS) == set(available)
    assert 'UUID_UPPERCASE_TEXT = "123E4567-E89B-12D3-A456-426614174000"' in text
    assert 'UUID_TEXT.toUpperCase()' not in text
    assert 'contains(UUID_UPPERCASE_TEXT)' in text
    assert '.map(AuthenticationContext::wireValue)' in text and '.map(Sha256Hex::wireValue)' in text
    assert '.map(RelativePath::wireValue)' in text and '.map(DisplayPath::wireValue)' in text
    assert plan['expectedFactoryAssertionsReplaced'] == 7 and plan['uppercaseRedactionAssertionsAdded'] == 1
    directory = snapshot/'src/schubert-nk-protocol/target/test-classes'
    physical = {}
    for file in sorted((directory/'dev/codex/schubert/nk/protocol/layout').glob('SemanticFieldValueTest*.class')):
        entry = str(file.relative_to(directory))
        assert decode(file.read_bytes(),entry)['sourceFile'] == 'SemanticFieldValueTest.java'
        physical[str(file)] = data.sha(file.read_bytes())
    assert len(physical) == 2
    tc = data.ROOT.parent/'toolchain'
    cpfile = snapshot/'src/schubert-nk-protocol/target/pgpt-test-classpath.txt'
    libraries = cpfile.read_text().strip().split(os.pathsep)
    allowed = tuple(str(tc/'m2/repository'/group)+'/' for group in ('org/jspecify','org/junit','org/opentest4j','org/apiguardian'))
    assert libraries and all(p.startswith(allowed) and Path(p).is_file() and not Path(p).is_symlink() for p in libraries)
    launcher = tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    assert data.sha(launcher.read_bytes()) == '0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    agent = tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    protocol = Path(normal['jars']['protocol']['path'])
    assert data.sha(protocol.read_bytes()) == normal['jars']['protocol']['sha256']
    dependencies = {str(p):data.sha(Path(p).read_bytes()) for p in [protocol,*libraries,launcher,agent]}
    main_classes = {}
    with zipfile.ZipFile(protocol) as jar:
        for name in jar.namelist():
            if not name.endswith('.class'):
                continue
            assert name.startswith('dev/codex/schubert/nk/protocol/') and '..' not in Path(name).parts
            main_classes[name] = data.sha(jar.read(name))
    assert len(main_classes) > 150
    helper = data.ROOT/'tools/quality/architecture/ProtocolSemanticJunitLauncher.java'
    helper_text = helper.read_text()
    assert all(BINARY+'#'+method in helper_text for method in METHODS)
    assert 'EXPECTED_TESTS = 4;' in helper_text and 'Set.of("ja-JP", "tr-TR")' in helper_text
    assert 'junit.jupiter.extensions.autodetection.enabled' in helper_text
    assert not any(word in helper_text for word in ('Class.forName','selectPackage(', 'scanClasspath', 'WebStartupGraph', 'ApiStartupGraph'))
    cases = [dict(className=BINARY,method=m,testId='PT-PRO-SEM-'+('D','N','V','Z')[i],
        canonicalOwner='WBS-P001-03',path=TEST,sourceSha256=hashes[TEST]) for i,m in enumerate(METHODS)]
    spec = data.ROOT/'evidence/01_PT/001_NK-PRO-001/1187_Semantic独立期待値七・診断保護・定数九PGPT仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        expectedTestsPerLocale=4,expectedSuitesPerLocale=1,locales=['ja-JP','tr-TR'],expectedUniqueMethods=4,
        normalSnapshot=str(snapshot),allCurrentSourceInputHashes=hashes,physicalTestFiles=physical,
        completeProtocolMainClasses=main_classes,dependencyHashes=dependencies,libraryClasspath=libraries,
        launcherJar=str(launcher),jacocoAgent=str(agent),protocolJar=str(protocol),testClassesDirectory=str(directory),
        helperPath=str(helper),helperSha256=data.sha(helper.read_bytes()),specPath=str(spec.relative_to(data.ROOT)),specSha256=data.sha(spec.read_bytes()),
        judgement='PT_DEFAULT_CONCRETE_REVIEW_PURE_VALUES_NO_HELD_OPERATIONS',actualNetworkPermitted=False,
        actualDatabasePermitted=False,actualVmRootServicePermitted=False,heldTestExtraction=False,
        newTestFixtureHarnessForHeldOperations=False,productTestsExecuted=0,coverage=None,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

