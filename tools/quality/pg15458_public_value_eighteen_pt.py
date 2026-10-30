"""Four original whole suites18; six memory-only targets and two own public test outputs."""
import hashlib
import re
import shutil
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
MAIN_PINS={"maintenance/InspectorSettings":"5fe7308a07bd1647aea4981749e348c44913e1f5df73159865f502be98bc24ae","logging/RequestLogDetails":"96467f5d3475d8e2fe5fe02124ce7d8571403f9141527a87ea880c9640117aa1","application/question/QuestionReceiptId":"32e2d84c19a05c4655c6911e0b27374c13fb6b4d3ef09ead40e60877305d5d2f","application/question/QuestionReceiptIdGenerator":"a4cb4c03f5dbdb225632d6abf4c2465fbb414ce09b0894f0b6649c83c7bc145d","application/question/StubAnswerProvider":"719addcd16754a2179b04a31ec7a17130c912fef362adbcbcc347ec523f4816f","application/question/AnswerResult":"bfa7c5a2827d5c97579a030df72997f928f5817b6d68ea9b0d918d88aef3fae6"}
DECLARED={"maintenance/InspectorSettingsTest":["0184124b8740a45322de685b4b9be4ff6705818dd259a5c15db78ef47de6faff",3],"logging/RequestLogDetailsTest":["c266b46400912485549e57220b73e94cae7ef4304d13871afeee7f7f5248e184",2],"application/question/QuestionReceiptIdTest":["95ecae1fb73ba439d3150b37083f087fde857f49dfa7a1c0e67f5bf4ac69e1c3",8],"application/question/StubAnswerProviderTest":["ac4d482aeaa66f017973eddcff1858990a7ef4d3f07ca03138c1a1ebf6f2dceb",5]}
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
SESSION='PG15458-PUBLIC-VALUE-CURRENT-WHOLE18'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PUBLIC_OUTPUTS={
'target/question-receipt-traces/PT-QST-RID008.txt':'forward=0123456789ABCDEFGHJKMNPQRS\nreverse=ZYXWVTSRQPNMKJHGFEDCBA9876\nlength=26\nalphabetSize=32\nrandomDrawsPerId=26\nownerOrTimeInput=false\n',
'target/question-stub-traces/PT-ASY-STB005.txt':'provider=STUB\nanswerLength=0\nclockReadsPerCall=1\nconcurrentCalls=64\nuniqueClockValues=64\nexternalCalls=0\nrawBodySaved=false\n'}
if __name__=='__main__':
    invocation=capture(__file__)
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15458-public-value-eighteen-pt-v1';run.OUT=run.host.BASE/'PG15458-public-value-eighteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/PublicValueCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['InspectorSettingsTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='1fc2b5de22456d9f09ce637d857651d99cfc1eb0785cd8a16731bb2c05470284'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15442-current1810-auth-context-codec-registry-v1/manifest.json','e94941427a78ea47d0b82eabbcffd19400909efb16b939c3216a30cc6aed897c')
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','TemporaryInfrastructureException','System.getenv(','getConnection('])
        assert ('dev.codex.schubert.nk.api.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
        if 'Files.' in text:
            assert name in {'QuestionReceiptIdTest','StubAnswerProviderTest'} and text.count('Files.')==2 and 'Files.createDirectories(directory)' in text and 'Files.writeString(' in text
        else:assert name in {'InspectorSettingsTest','RequestLogDetailsTest'}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}=={name}
    run.step=environmental_step
    try:run.main()
    except SystemExit as terminal:
        if terminal.code!=0:raise
    outputs={}
    for relative,expected in PUBLIC_OUTPUTS.items():
        path=run.SLOT/relative
        assert path.is_relative_to(run.SLOT) and not path.is_symlink() and path.read_bytes()==expected.encode('ascii')
        destination=run.OUT/path.name;shutil.copyfile(path,destination)
        outputs[relative]=dict(sha256=hashlib.sha256(expected.encode('ascii')).hexdigest(),bytes=len(expected.encode('ascii')),publicFixtureOnly=True,copy=str(destination.relative_to(data.ROOT)))
    verify(invocation)
    data.write(run.OUT/'public-test-output.safe.json',dict(actualExit=0,source=SOURCE,invocation=invocation,originalManifestSha256=run.host.sha(run.OUT/'manifest.json'),outputs=outputs,productFileOperations=False,testOwnNewSlotPublicEvidenceWrites=True))
    print('public_outputs='+str(len(outputs)))
