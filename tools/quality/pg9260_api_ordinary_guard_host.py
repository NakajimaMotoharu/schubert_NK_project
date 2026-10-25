"""Two existing ordinary methods missing current qualification; no install/native/HookDriver."""
import re
import scoped_prometheus_host as run

SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
COMPILE=run.host.W/'pg9246-web-life-lock-six-compile-v1'
COMPILE_SHA='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
COUNTS={'ApiProcessLifetimeTest':2}
METHODS={'ready004BorrowedDelegatesStopGuardAndActualDeliveryPreserved',
         'ready005HealthFailureInterruptedAndNormalStopDistinct'}

if __name__=='__main__':
    run.SOURCE=SOURCE; run.COMPILE=COMPILE; run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9260-api-ordinary-guard-host-v1'
    run.OUT=run.host.BASE/'PG9260-api-ordinary-guard-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiOrdinaryGuardJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetimeTest.java'
    run.TEST_SOURCE_OVERRIDES={}; run.EXTRA_TEST_SOURCES=(); run.COUNTS=COUNTS
    run.SESSION_ID='PG9260-API-ORDINARY-GUARD'; run.FIXTURES={}
    helper=''.join(run.HELPER.read_text().split())
    assert 'selectClass' not in helper
    assert set(re.findall(r'DiscoverySelectors.selectMethod\(types.getFirst\(\),"([^"]+)"\)',helper))==METHODS
    assert helper.count('DiscoverySelectors.selectMethod(')==2
    assert all(helper.count(name+'==2')==1 for name in (
      'value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()'))
    source=run.NEW_TEST.read_text()
    matches=re.findall(r'(?ms)^  @Test\n  void (ready00[45]\w+)\(.*?^  }',source)
    bodies=re.findall(r'(?ms)^  @Test\n  void ready00[45]\w+\(.*?^  }',source)
    assert set(matches)==METHODS and len(bodies)==2
    fixture=source[source.index('  private static WireMessage<FixedPayload> event()'):source.index('  @Test\n  void ready004')]
    for body in [*bodies,fixture]:
        assert all(token not in body for token in ('.install(','.main(','HookDriver','ProcessBuilder','Runtime.getRuntime','new ApiProcessMain'))
    run.main()
