"""Current source original Outbox whole13; plain values/one-level JDK cause only, no dispatch or graph."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'OutboxPolicyTest':4,'OutboxModelTest':4,'OutboxDlqMetadataTest':2,'OutboxDispatchReportBoundaryTest':3}
SESSION='PG15346-CURRENT-OUTBOX-WHOLE13'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"OutboxPolicyTest":"ddd94d17ece3c2ed0861cd21f463920ed5972c39102f60f147ee8c45f2e5abc6","OutboxModelTest":"61827ab290718de21cf8f4c6ec33758d484af5a12638c33efff28d6eaba5fe18","OutboxDlqMetadataTest":"54683e12417a392faffe354584412111e7713da8a17d3b4ac0d4428358c6c47c","OutboxDispatchReportBoundaryTest":"19d79b9b2d1c49b87b1d56df39f6bd4d37103403cca4311541bfdf741e440ffc"}
MAIN_PINS={"OutboxDestination":"8ab0216109c17c6d5cf96039b6ac968dd2cb6fc401c2f93b0f92cc08c3ed8e80","OutboxRetrySchedule":"f565b0413b5e262907e209f523915e3050beb7062fec3b369d178124c58e8854","OutboxEntry":"09bb3b7767c6c09c5c8685088a7ef0494898aedc478307cbd44a14cfa7dd0ef4","OutboxRequest":"564190205500c14866882d60d36d654276562f38593229ef85c14da0ef7ab463","OutboxDlqMetadata":"ef0be1f11629947394710ce2f537567c19401737e2329a3d54719471ea5b7f53","OutboxDispatchReport":"c9ba13a64c580fea33b744134a5534d44142233f72a28c40d5cc0442e2fc472f","OutboxIntegrityException":"56a5f3af8ccf296acef3aa0991920755756862223d6ea1c111e248448d63941a","OutboxSendException":"b2dac8539f303d4b2677bf78369f1bc9c77ad5c37c863633b968f187adb8a210"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15346-current-outbox-thirteen-pt-v1';run.OUT=data.BASE/'PG15346-current-outbox-thirteen-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalCurrentOutboxThirteenJunitLauncher.java';run.NEW_TEST=TESTS['OutboxModelTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='OutboxModelTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15331-current1760-exact11-owner-registry-v3/manifest.json','cfb7c63e1b0761397371bf5fef625b7014aff588b992c35619c99b633374bd9f')
    assert not {'dev.codex.schubert.nk.api.messaging.outbound.'+name for name in COUNTS}&set(registry['suiteNames'])
    prefix='dev/codex/schubert/nk/api/messaging/outbound/'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,pin in MAIN_PINS.items():
            target=prefix+name;main='src/schubert-nk-api/src/main/java/'+target+'.java'
            assert target not in registry['fullSourceUnits']
            assert normal['begin']['inputHashes'][main]==run.host.sha(data.ROOT/main)==run.host.sha(COMPILE/'snapshot'/main)==pin
            assert {p[:-6] for p in jar.namelist() if p==target+'.class' or p.startswith(target+'$') and p.endswith('.class')}=={target}
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert len(re.findall(r'@Test\b',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','FileSystems.','getFileStore(','Linux','getenv(','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','TemporaryInfrastructureException','getSuppressed(','@BeforeAll','@BeforeEach','@TempDir','getConnection(','DataSource','PreparedStatement','.production('])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert not re.search(r'(?<![A-Za-z0-9_])Files\s*\.',text)
        assert '"dev.codex.schubert.nk.api.messaging.outbound.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
        assert 'new ApiProcessMain(' not in text and '.run(' not in text and '.main(' not in text
    run.step=environmental_step;run.main()
