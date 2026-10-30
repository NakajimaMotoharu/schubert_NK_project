"""Original API admitted-config/readiness11; static fake data and suppliers only, no main/run/native."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"ApiAdmittedConfigurationTest":8,"ApiReadinessPredicateTest":3}
SESSION='PG15300-ORIGINAL-API-CONFIG-READINESS11'
ROOT=data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"ApiAdmittedConfigurationTest":"63d82faa7692112a050e39ea6a15418f7de3edfb252f059f0220310dd66902cf","ApiReadinessPredicateTest":"f6331acd7c4afdfa0ff027d3020784605347149b75c3526118c20a8270e67dcc"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15300-api-config-readiness-eleven-pt-v1';run.OUT=data.BASE/'PG15300-api-config-readiness-eleven-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalApiConfigReadinessJunitLauncher.java';run.NEW_TEST=TESTS['ApiAdmittedConfigurationTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='ApiAdmittedConfigurationTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15284-current1748-profile-terminal-registry-v1/manifest.json','7bc09027b74939ddc45fb92d63bb82be1c096f898670f275bed940cbe507435d')
    assert not {'dev.codex.schubert.nk.api.bootstrap.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.api.bootstrap.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    files_call=re.compile(r'(?<![A-Za-z0-9_])Files\s*\.')
    assert not files_call.search('ServiceConfigFiles.Service.WEB') and all(files_call.search(v) for v in ['Files.readString(x)','java.nio.file.Files.readString(x)','Files.delete(x)'])
    assert not files_call.search(TESTS['ApiAdmittedConfigurationTest'].read_text())
    assert all('new ApiProcessMain(' not in p.read_text() and '.run(' not in p.read_text() and '.main(' not in p.read_text() for p in TESTS.values())
    run.step=environmental_step;run.main()
