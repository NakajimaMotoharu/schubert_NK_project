"""Necessary single-exec full Catalog source qualification: four unchanged whole suites, no union of earlier execs."""
import re
import pg14466_api_web_catalog_whole_twenty_eight_pt as catalog
import pg14472_api_web_scrape_whole_twenty_eight_pt as scrape
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={**catalog.COUNTS,**scrape.COUNTS}
SESSION='PG14556-ORIGINAL-CATALOG-SCRAPE56-SINGLE-EXEC'
ROOT=catalog.ROOT
TESTS={**catalog.TESTS,**scrape.TESTS}
PINS={**catalog.PINS,**scrape.PINS}
FIXTURES={'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt': '1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14556-catalog-scrape-single-exec-fifty-six-pt-v1'
    run.OUT=run.host.BASE/'PG14556-catalog-scrape-single-exec-fifty-six-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/OriginalCatalogScrapeSingleExecJunitLauncher.java'
    run.NEW_TEST=TESTS['ApiMetricCatalogTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ApiMetricCatalogTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal('])
        assert '"dev.codex.schubert.nk.'+('api.' if name.startswith('Api') else 'web.')+'monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.step=environmental_step
    run.main()
