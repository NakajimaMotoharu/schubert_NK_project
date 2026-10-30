"""Original joint Web exporter62: new48 and necessary repeated14 for same-exec full Source, no external actions."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"WebCounterMetricExporterTest":16,"WebGaugeMetricExporterTest":16,"WebDurationMetricExporterTest":16,"WebMetricScrapeTest":14}
SESSION='PG15042-ORIGINAL-WEB-EXPORTER62'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"WebCounterMetricExporterTest":"6528fc4e4b9cb3e14ebf1d5758486a2891dfb339b6ad645538134ca0e48aae97","WebGaugeMetricExporterTest":"599204f98beb1b1bc85f1e8c5489d61a721cd7092eed9dbe5acd651024bed6a3","WebDurationMetricExporterTest":"104ea8495b9ca104d8565a9ea20fd2765d5489abe479133dd9a642131814ffab","WebMetricScrapeTest":"0670d54591dac96404e460698fff479f7526f7feda2b347e0a1d31dd6832b187"}
FIXTURES={'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt':'1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15042-web-exporter-joint-sixty-two-pt-v1';run.OUT=data.BASE/'PG15042-web-exporter-joint-sixty-two-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalWebExporterJointJunitLauncher.java';run.NEW_TEST=TESTS['WebCounterMetricExporterTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='WebCounterMetricExporterTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15026-current1319-batch-standard-registry-v1/manifest.json','4b1299e57ecb5616727e338e0ef8bc080e5b38fb70c61bd1789df696aebbfbe0')
    assert {'dev.codex.schubert.nk.web.monitoring.'+name for name in COUNTS}&set(registry['suiteNames'])=={'dev.codex.schubert.nk.web.monitoring.WebMetricScrapeTest'}
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','Files.','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system','OutOfMemoryError'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.web.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step;run.main()
