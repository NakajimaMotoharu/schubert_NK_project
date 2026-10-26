"""Closed seven-class catalog: new valid page/state projections and related existing cases only."""
import json
from pathlib import Path
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10042_user_sql_preflight import CATALOG as USER
from pg10064_log_sql_preflight import CATALOG as LOG
from pg10078_question_sql_preflight import CATALOG as QUESTION

SOURCE = 'dd138e9def675f9278ae4b1bdb8c5ee3e34f2b77'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10100-query-batch-six-compile-v1/snapshot'
OUT = data.BASE/'PG10102-query-batch-preflight-v1'
PREFIX = 'dev.codex.schubert.nk.api.application.'
CATALOG = {**{PREFIX+'admin.'+k:tuple(v) for k,v in USER.items()},
    **{PREFIX+'log.'+k:tuple(v) for k,v in LOG.items()},
    **{PREFIX+'question.'+k:tuple(v) for k,v in QUESTION.items()}}
NEW = {
    PREFIX+'admin.UserQuerySqlContractTest':('sql009FullPagePreservesAllFiftyRowsAndRequestedPage',),
    PREFIX+'log.LogSqlContractTest':('sql009FullHundredRowPageKeepsDescendingIds',),
    PREFIX+'question.QuestionSqlContractTest':('sql009ValidProcessingCancelledAndFiveErrorCodesRemainTypedData',
        'sql010FullQuestionPagePreservesFiftyUnansweredRows')}
CATALOG = {k:v+NEW.get(k,()) for k,v in CATALOG.items()}
SUBJECTS = {'dev/codex/schubert/nk/api/application/admin/UserQueryRequest',
    'dev/codex/schubert/nk/api/application/log/LogRequest',
    'dev/codex/schubert/nk/api/application/question/QuestionQueryRequest',
    *{'dev/codex/schubert/nk/api/persistence/'+name+'QueryRepository' for name in ('User','Log','Question')}}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10100-query-batch-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT)
    assert len(CATALOG) == 7 and sum(map(len,CATALOG.values())) == 52 and sum(map(len,NEW.values())) == 4
    cases,physical_test = [],{}
    for binary,methods in CATALOG.items():
        simple = binary.rsplit('.',1)[-1]
        path = 'src/schubert-nk-api/src/test/java/'+binary.replace('.','/')+'.java'
        text = (data.ROOT/path).read_text()
        assert tuple(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)) == methods
        assert not any(marker in text for marker in (
            'BeforeAll','BeforeEach','AfterAll','AfterEach','TempDir','Disabled','ExtendWith','RegisterExtension',
            'java.net','java.nio.file','javax.crypto','jakarta.jms','ApiLogDatabaseFixture','UserApplicationFixture',
            'TemporaryInfrastructureException','WebStartupException','DataSource','DriverManager','jdbc:',
            'FingerprintKeyRing','ResponseSnapshotCodec','SessionPayloadCodec','Executors','new Thread',
            'getDeclared','setAccessible','Class.forName','new SQLException','new ProcessBuilder','Runtime.getRuntime',
            'throw new IllegalStateException','assertThrows(RuntimeException.class'))
        code = ''.join(m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*')))
        if simple.endswith('SqlContractTest'):
            assert all('proxy('+name+'.class' in code for name in ('Connection','PreparedStatement','ResultSet'))
            assert code.count('Proxy.newProxyInstance(') == 1
            assert 'assertEquals(List.of("RS", "PS"), closed)' in text
            assert 'assertEquals(0, jdbc.connectionCalls)' in text
        else:
            assert all(re.fullmatch(r'null(?:,null){2,3}',q) for q in re.findall(r'\.query\(([^)]*)\)',code))
            assert '.close(' not in code
        target = NORMAL/'src/schubert-nk-api/target/test-classes'/(binary.replace('.','/')+'.class')
        declaration = decode(target.read_bytes(),binary.replace('.','/')+'.class')
        assert declaration['sourceFile'] == simple+'.java'
        for method in methods:
            assert len([m for m in declaration['methods'] if m['name'] == method and m['descriptor'] == '()V' and m['hasCode']]) == 1
        files = {str(p):data.sha(p.read_bytes()) for p in target.parent.glob(simple+'*.class')}
        expected = {str(target)}
        if simple.endswith('SqlContractTest'):
            expected.update(str(target.with_name(simple+suffix+'.class')) for suffix in ('$Call','$Jdbc'))
        assert set(files) == expected
        physical_test.update(files)
        cases.extend(dict(className=binary,method=m,path=path,sourceSha256=hashes[path],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=SOURCE,
            newTestIdInThisGroup=m in NEW.get(binary,()),oldDynamicResultTransferred=False) for m in methods)
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    with zipfile.ZipFile(jar) as archive:
        physical_main = {n:data.sha(archive.read(n)) for n in archive.namelist()
            if any(n == subject+'.class' or n.startswith(subject+'$') for subject in SUBJECTS)}
    expected = {n+'.class' for n in SUBJECTS}|{'dev/codex/schubert/nk/api/persistence/QuestionQueryRepository$RowMapper.class'}
    assert set(physical_main) == expected and len(physical_main) == 7 and len(physical_test) == 13
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),expectedTests=len(cases),expectedSuites=len(CATALOG),
        caseCounts={k:len(v) for k,v in CATALOG.items()},casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        physicalTestFiles=physical_test,physicalMainClasses=physical_main,completeMainSourceUnits=sorted(SUBJECTS),
        allCurrentSourceInputHashes=hashes,newTestIds=4,relatedRegressionMethods=48,
        standaloneFixtureSourceReviewed=True,realConnectionConstructed=False,
        connectionKind='PUBLIC_INTERFACE_PROXY_NO_BACKEND',hmacOrJceInvoked=False,sharedDbFixturesInvoked=False,
        graph9ExecutionRequested=False,keyCloseValidationRetried=False,productTestsExecuted=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=len(cases),suites=len(CATALOG),physicalMainClasses=len(physical_main),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
