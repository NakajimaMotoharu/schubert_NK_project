"""Original fixed service argv5; strings/profile enum/Value only, no execution or authority."""
import re
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={"FixedServiceExecArgumentsTest":5}
SESSION='PG15259-ORIGINAL-FIXED-SERVICE-ARGV5'
ROOT=data.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={"FixedServiceExecArgumentsTest":"a6661ae17848c62d35fafed8804e220c5b673bb4437c2f5e73ce81c64651b569"}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15259-fixed-service-argv-five-pt-v2';run.OUT=data.BASE/'PG15259-fixed-service-argv-five-pt-v2'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalFixedServiceArgvJunitLauncher.java';run.NEW_TEST=TESTS['FixedServiceExecArgumentsTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='FixedServiceExecArgumentsTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    registry=data.read_checked(data.BASE/'PG15248-current1729-stop-budget-registry-v1/manifest.json','64e5758fc7b382c109741c9f97d291b746046b6446e6befc4beb07c6c662c8bd')
    assert not {'dev.codex.schubert.nk.bootstrap.'+name for name in COUNTS}&set(registry['suiteNames'])
    for name,path in TESTS.items():
        relative=str(path.relative_to(data.ROOT));assert normal['begin']['inputHashes'][relative]==run.host.sha(path)==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        text=path.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['ProcessBuilder','DriverManager','FileSystems.','getFileStore(','Linux','getenv(','import java.sql','EmbeddedActiveMQ','ActiveMQConnectionFactory','ServiceProcessResources','preserveFatal(','Class.forName(','HttpClient','Clock.system'])
        assert not re.search(r'\.\s*(?:gc|setVerbose|dumpHeap)\s*\(',text)
        assert '"dev.codex.schubert.nk.bootstrap.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    files_call=re.compile(r'(?<![A-Za-z0-9_])Files\s*\.')
    assert not files_call.search('ServiceConfigFiles.Service.WEB') and all(files_call.search(v) for v in ['Files.readString(x)','java.nio.file.Files.readString(x)','Files.delete(x)'])
    assert not files_call.search(TESTS['FixedServiceExecArgumentsTest'].read_text())
    assert run.host.sha(data.ROOT/'tools/quality/pg15258_fixed_service_argv_five_pt.py')=='46eff1b10c386b333f23819d2ed0ea2c315de911e36c28d30105d2380f77cca5'
    run.step=environmental_step;run.main()
