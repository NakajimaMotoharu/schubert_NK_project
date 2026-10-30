"""Four original Inbox value suites15; public HMAC/bounded memory/scope values, no DB or snapshot codec."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/api/'
MAIN_PINS={"idempotency/OperationFingerprint":"25f0c77746cdb01ce938f83fe0b019929f0aeb2e073db4f043abb3a41ba0995b","idempotency/CanonicalRequest":"ae5d61f51e59329ffcccf18c702a430fc15d4e3731b2ffb5544ec9788a4ba2eb","idempotency/CanonicalField":"427b37bf360f201bd1509e336aa435f2a1db77c9f782b842aa2bf16fdcc28e3a","idempotency/WipingByteArrayOutputStream":"1f751a0267c7d9f894806d67e5b9b3c05955038353d6f6bd6a44cfe3bd1217de","idempotency/QuestionQueryScopeFrame":"77b626a3d396b6e6e98b2199149e8892dfa2dd478a21759b0d20cbb072988b2e","idempotency/ResponseSnapshotIdentity":"66e9e45738d02de02e8c0d336e997c2e2878f96e1620d84ae532c663ebd3418c","idempotency/InboxRequest":"5c4f01d72d17a234d201ee5de6e0a47fc5fed5be4d328b4f283544e0eaf69e1a","idempotency/InboxResultReference":"09e9911b5f5418013364fadeb3f70e9dae33cc0b2df8c06016ce8972a953ec20","idempotency/InboxResultReferenceType":"7f6747c6b267b81647554aa021ad95959a80dde08501e33b3488f14794c25568","idempotency/InboxCompletion":"bc5b5d44493484ae2a5264b2019c07f6eb2887c2fb4f93f3dea75b9605f52928","idempotency/InboxCompletionState":"fb20f0fda776d5ccfde69dd75e52b5bc5c6cc1d0e4ada0f2b04df99ffe6267b0","idempotency/InboxExecution":"1b791d1eab0c318582bb27ce37f9f99cbb590901c7d8c4f03a0daaf42f2c31c1","idempotency/InboxExecutionStatus":"349b9813318d93b15eb334a5ea5de8bd24f5cbfde96cec8114eafa8150aec7bb","idempotency/InboxException":"3d5cf68d628c17ccdb489e1c5199d43b144562d4b96df544580f7013eb1a680b"}
DECLARED={"idempotency/InboxModelTest":["bbb307fa4195d225ec4b4f4b4f20a8e911ebbf1418f52d8373b545d990f82aaf",5],"idempotency/OperationFingerprintTest":["6b76952a1d552a0d1a189c42c999435dc83439e94600a73f052f3a05b2069eeb",5],"idempotency/SecretBufferTest":["32743b02e36a6d15cc90d4510de108ccdc86f1ddb3e27920b2299b85566fbd32",3],"idempotency/QuestionQueryScopeFrameTest":["9a0872ab0b442ec299625c6ec33a6e1ef201d7a4258ce30128f4f2f30c31d7ca",2]}
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java'/PREFIX
TESTS={p.rpartition('/')[2]:ROOT/(p+'.java') for p in DECLARED}
COUNTS={p.rpartition('/')[2]:row[1] for p,row in DECLARED.items()}
PINS={p.rpartition('/')[2]:row[0] for p,row in DECLARED.items()}
FIXTURES={}
SESSION='PG15582-PUBLIC-INBOX-VALUES-CURRENT-WHOLE15'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15582-public-inbox-values-fifteen-pt-v1';run.OUT=run.host.BASE/'PG15582-public-inbox-values-fifteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/PublicInboxValuesCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['OperationFingerprintTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={name:path for name,path in TESTS.items() if name!=run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=='5c03328fd1c9ee475de7d6250fc175632dbac52a26e2786da42958c85eac6503'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    current=data.read_checked(data.BASE/'PG15572-current1879-public-session-codec-registry-v1/manifest.json','00dabafe1bbb8737a0ea9dc908f98e16c46a2743100d21164020f841082ef4d5')
    assert current['postDisclosureCorrections']['22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3']['effectiveDisclosure']['effectiveCryptoOrKeyOperationsInvoked'] is True
    def files_operation(text):return re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',text) is not None
    assert not files_operation('ServiceConfigFiles.Service.WEB')
    assert not files_operation('ServiceConfigFiles.Contents values')
    assert all(files_operation(v) for v in ['Files.readString(path)','java.nio.file.Files.readAllBytes(path)','Files \n .readString(path)'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(run.host.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','System.getenv(','getConnection(','TemporaryInfrastructureException','WebStartupException','Class.forName(','HttpClient','Tomcat','createConnection(','createContext(','createRetainingUnknown(','configureOwned(','.production('])
        assert not files_operation(text)
        assert ('dev.codex.schubert.nk.api.'+next(p for p in DECLARED if p.endswith('/'+name)).replace('/','.')) not in current['suiteNames']
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for short,pin in MAIN_PINS.items():
            name=PREFIX+short;path='src/schubert-nk-api/src/main/java/'+name+'.java'
            assert name not in current['fullSourceUnits'] and normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            expected={name,name+'$Reason'} if short=='idempotency/InboxException' else {name}
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==expected
    run.step=environmental_step;run.main()
