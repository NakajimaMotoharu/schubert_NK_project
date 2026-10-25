"""Pure exception callback owner binding, no JMS/DLQ/Hook or application startup."""
import re
import scoped_prometheus_host as run

SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
COMPILE=run.host.W/'pg9246-web-life-lock-six-compile-v1'
COMPILE_SHA='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
COUNTS={'ApiCommittedFatalBindingTest':2}
METHODS={'fatalBinding001CommittedEventStopsOwnerAndAwaitRemainsSanitizedNonSuccess',
         'fatalBinding002CallbackRemainsBoundToItsOwnerAndNeverReadsFailurePayload'}

if __name__=='__main__':
    run.SOURCE=SOURCE; run.COMPILE=COMPILE; run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9272-api-fatal-callback-host-v1'
    run.OUT=run.host.BASE/'PG9272-api-fatal-callback-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiFatalCallbackJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiCommittedFatalBindingTest.java'
    run.TEST_SOURCE_OVERRIDES={}; run.EXTRA_TEST_SOURCES=(); run.COUNTS=COUNTS
    run.SESSION_ID='PG9272-API-FATAL-CALLBACK'; run.FIXTURES={}
    helper=''.join(run.HELPER.read_text().split())
    assert 'List.of("dev.codex.schubert.nk.api.bootstrap.ApiCommittedFatalBindingTest")' in helper
    assert all(helper.count(name+'==2')==1 for name in (
      'value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()'))
    source=run.NEW_TEST.read_text()
    assert source.count('@Test')==2 and set(re.findall(r'void (fatalBinding\w+)\(',source))==METHODS
    assert all(token not in source for token in ('.install(','.main(','Runtime.getRuntime','ProcessBuilder',
      'HookDriver','new ApiProcessMain','InitialContext','DriverManager','ConnectionFactory'))
    run.main()
