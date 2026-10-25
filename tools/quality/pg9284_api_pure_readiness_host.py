"""Only pure BooleanSupplier predicates, never construct or start Main or HTTP."""
import re
import scoped_prometheus_host as run

SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
COMPILE=run.host.W/'pg9246-web-life-lock-six-compile-v1'
COMPILE_SHA='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
COUNTS={'ApiReadinessPredicateTest':3}
METHODS={'health001LiteralTruthTablesAndShortCircuitOrder',
         'health002EveryCallReadsCurrentStateWithoutLatchingSuccess',
         'health003NullAndExactFailureAreNeverConvertedToHealth'}

if __name__=='__main__':
    run.SOURCE=SOURCE; run.COMPILE=COMPILE; run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9284-api-pure-readiness-host-v1'; run.OUT=run.host.BASE/'PG9284-api-pure-readiness-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiPureReadinessJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiReadinessPredicateTest.java'
    run.TEST_SOURCE_OVERRIDES={}; run.EXTRA_TEST_SOURCES=(); run.COUNTS=COUNTS
    run.SESSION_ID='PG9284-API-PURE-READINESS'; run.FIXTURES={}
    helper=''.join(run.HELPER.read_text().split())
    assert 'List.of("dev.codex.schubert.nk.api.bootstrap.ApiReadinessPredicateTest")' in helper
    assert all(helper.count(name+'==3')==1 for name in (
      'value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()'))
    source=run.NEW_TEST.read_text()
    assert source.count('@Test')==3 and set(re.findall(r'void (health\w+)\(',source))==METHODS
    assert all(token not in source for token in ('.install(','.main(','.run(','new ApiProcessMain',
      'Runtime.getRuntime','ProcessBuilder','HookDriver','HttpServer','Socket','DriverManager','ConnectionFactory'))
    run.main()
