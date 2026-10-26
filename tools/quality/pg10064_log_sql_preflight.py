"""Freeze eight ordinary plain-field/response methods, with null-only repository calls."""
import json
from pathlib import Path
import re
import subprocess
import zipfile

import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

ROOT = data.ROOT
SOURCE = '6cd6ae7efc495f17e1ebb79291f26c7a90f99dc7'
NORMAL = ROOT.parent/'pgpt-runs/PG379/pg10062-log-sql-six-compile-v1/snapshot'
OUT = data.BASE/'PG10064-log-sql-preflight-v1'
SUBJECTS = {'dev/codex/schubert/nk/api/application/log/LogRequest',
    'dev/codex/schubert/nk/api/persistence/LogQueryRepository'}
PREFIX = 'dev.codex.schubert.nk.api.application.log.'
CATALOG = {
    'LogPlainContractTest':(
        'plain001AbsentFieldsAndOriginalPageHaveLiteralMetadata',
        'plain002FilledFieldsPreserveUtf8OriginalFiltersAndUtcDates',
        'plain003MalformedLayoutLengthEnumDatesAndReservedAreRejected',
        'plain004NullPublicBoundariesStopBeforeAnyRepositoryReceiver',
        'plain005EmptyResponseClampsRequestedPageWithoutChangingCanonicalPage',
        'plain006WrongPageSizeAndRecordCountNeverAcceptNpeAsSuccess',
        'plain007WrongResponseLayoutAndNonPagedDataAreRejected',
        'plain008AllSevenOptionalPresenceMasksUseIndependentExpectedValues'),
    'LogSqlContractTest':(
        'sql001EmptySearchRetainsRequestedPageAndStableSql',
        'sql002AllFilterMasksBindLiteralWildcardsAndUtcBounds',
        'sql003MinimalMappedRowKeepsOptionalAbsenceAndMilliseconds',
        'sql004FullMappedRowMatchesIndependentFixedWidthGolden',
        'sql005FinalPageClampHasExactHundredRowBoundaries',
        'sql006InvalidInputStopsBeforeBorrowedReadOnlyBlock',
        'sql007UserRoleDeniedBeforeAnyJdbcMethod',
        'sql008NullArgumentsStopWithoutInterfaceCalls')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10062-log-sql-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    cases,physical_test = [],{}
    for simple,methods in CATALOG.items():
        binary = PREFIX+simple
        path = 'src/schubert-nk-api/src/test/java/'+binary.replace('.','/')+'.java'
        text = (ROOT/path).read_text()
        assert tuple(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)) == methods
        assert not any(marker in text for marker in (
            'BeforeAll','BeforeEach','AfterAll','AfterEach','TempDir','Disabled','ExtendWith','RegisterExtension',
            'java.net','java.nio.file','javax.crypto','jakarta.jms','UserQueryRequestTest.',
            'UserMutationRequestTest.','ApiLogDatabaseFixture','UserApplicationFixture','TemporaryInfrastructureException',
            'WebStartupException','DataSource','DriverManager','FingerprintKeyRing',
            'ResponseSnapshotCodec','SessionPayloadCodec','Executors','new Thread','Class.forName','getDeclared'))
        code = ''.join(m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*')))
        queries = re.findall(r'\.query\(([^)]*)\)',code)
        if simple == 'LogSqlContractTest':
            assert all('proxy('+name+'.class' in code for name in ('Connection','PreparedStatement','ResultSet'))
            assert code.count('Proxy.newProxyInstance(') == 1
            assert not any(marker in text for marker in ('jdbc:', 'new SQLException', 'throw new IllegalStateException',
                'getDeclared', 'setAccessible', 'Class.forName', 'executeUpdate', 'new ProcessBuilder', 'Runtime.getRuntime'))
            assert 'assertEquals(List.of("RS", "PS"), closed)' in text
            assert 'assertEquals(0, jdbc.connectionCalls)' in text
        else:
            assert queries == ['null,null,null'] and '.close(' not in code
            assert '"REQUEST:LGSREQ01"' in text and '"999999"' in text
        assert 'newbyte[656]' in code and '"000001100"' in text
        assert 'assertThrows(RuntimeException.class' not in text
        target = NORMAL/'src/schubert-nk-api/target/test-classes'/(binary.replace('.','/')+'.class')
        declaration = decode(target.read_bytes(),binary.replace('.','/')+'.class')
        assert declaration['sourceFile'] == simple+'.java'
        for method in methods:
            found = [m for m in declaration['methods'] if m['name'] == method and m['descriptor'] == '()V' and m['hasCode']]
            assert len(found) == 1
        files = {str(p):data.sha(p.read_bytes()) for p in target.parent.glob(simple+'*.class')}
        expected_files = {str(target)}
        if simple == 'LogSqlContractTest':
            expected_files.update(str(target.with_name(simple+suffix+'.class')) for suffix in ('$Call','$Jdbc'))
        assert set(files) == expected_files
        physical_test.update(files)
        cases.extend(dict(className=binary,method=m,path=path,sourceSha256=hashes[path],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=SOURCE,oldDynamicResultTransferred=False) for m in methods)
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    with zipfile.ZipFile(jar) as archive:
        physical_main = {n:data.sha(archive.read(n)) for n in archive.namelist()
            if any(n == subject+'.class' or n.startswith(subject+'$') for subject in SUBJECTS)}
    assert set(physical_main) == {subject+'.class' for subject in SUBJECTS} and len(cases) == 16
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),expectedTests=16,expectedSuites=2,
        caseCounts={PREFIX+k:len(v) for k,v in CATALOG.items()},casesSha256=data.sha((OUT/'cases.json').read_bytes()),physicalTestFiles=physical_test,
        physicalMainClasses=physical_main,completeMainSourceUnits=sorted(SUBJECTS),allCurrentSourceInputHashes=hashes,
        standaloneFixtureSourceReviewed=True,realConnectionConstructed=False,connectionKind='PUBLIC_INTERFACE_PROXY_NO_BACKEND',
        hmacOrJceInvoked=False,sharedDbFixturesInvoked=False,graph9ExecutionRequested=False,
        keyCloseValidationRetried=False,normalCleanupOnlyNotLifetimeValidation=True,
        productTestsExecuted=0,newTestIds=8,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=len(cases),suites=len(CATALOG),mainClasses=len(physical_main),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
