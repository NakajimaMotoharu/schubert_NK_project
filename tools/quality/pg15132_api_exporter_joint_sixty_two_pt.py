"""Original joint API exporter62: new48 and necessary repeated14 for same-exec full Source, no external actions."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"ApiScalarMetricExporterTest":24,"ApiDurationMetricExporterTest":24,"ApiMetricScrapeTest":14}
SESSION='PG15132-ORIGINAL-API-EXPORTER62'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"ApiScalarMetricExporterTest":"a86dfd5d6989ad6248041a18b65b0812da2678838c83d3059e73d414df0287d5","ApiDurationMetricExporterTest":"be8d7f91cbfbd752446ad5385436e4b5c6e0cd47a63f5868a5d2c7b2870a23ec","ApiMetricScrapeTest":"eb3c35e5ffbe0eada68aacce03f744b3b2eabadcb531a3810e234600585dfc89"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15132-api-exporter-joint-sixty-two-pt-v1';run.OUT=data.BASE/'PG15132-api-exporter-joint-sixty-two-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalApiExporterJointJunitLauncher.java';run.NEW_TEST=TESTS['ApiScalarMetricExporterTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ApiScalarMetricExporterTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15122-current1567-api-pool-registry-v1/manifest.json','abcda0a7df5caf74ad7d419638df817a59811cb86dbc87d0d8a177b9ef8767c5')
    assert {'dev.codex.schubert.nk.api.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])=={'dev.codex.schubert.nk.api.monitoring.ApiMetricScrapeTest'}
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.api.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
