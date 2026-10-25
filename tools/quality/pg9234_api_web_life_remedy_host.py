"""Impact 10+1 and new ordinary Web3 only; no native HookDriver or application Main selected."""
import re
import scoped_prometheus_host as run

SOURCE='600b966bab415690bf09d24ba07268a097b19d18'
COMPILE=run.host.W/'pg9232-api-web-life-remedy-six-compile-v1'
COMPILE_SHA='38ea73ddb99188202104086355e365e61be103eb5f8abc383dfab975f879e219'
COUNTS={'ApiProcessLifetimeTest':10,'ApiProcessObservationFactoryTest':1,'WebLifetimeOrdinaryCloseTest':3}

if __name__=='__main__':
    run.SOURCE=SOURCE; run.COMPILE=COMPILE; run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9234-api-web-life-remedy-host-v1'
    run.OUT=run.host.BASE/'PG9234-api-web-life-remedy-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiWebLifeRemedyJunitLauncher.java'
    api=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api'
    web=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web'
    run.NEW_TEST=api/'bootstrap/ApiProcessObservationFactoryTest.java'
    run.TEST_SOURCE_OVERRIDES={
      'ApiProcessLifetimeTest':api/'bootstrap/ApiProcessLifetimeTest.java',
      'WebLifetimeOrdinaryCloseTest':web/'bootstrap/WebLifetimeOrdinaryCloseTest.java'}
    support=api/'monitoring'
    run.EXTRA_TEST_SOURCES=tuple(support/name for name in (
      'ApiFactoryObservationFixture.java','ApiReadOnlyObservationAttemptTest.java',
      'OutboxObservationRepositoryTest.java','DbPoolMetricObservationTest.java'))
    run.COUNTS=COUNTS; run.SESSION_ID='PG9234-API-WEB-LIFE-REMEDY'; run.FIXTURES={}
    helper=''.join(run.HELPER.read_text().split())
    assert 'selectClass' not in helper
    assert 'selectMethod(types.get(0),"lifeBudget"+' in helper
    assert 'selectMethod(types.get(1),"apiObsBoot009")' in helper
    assert 'selectMethod(types.get(2),"wlClose"+' in helper and 'i<=10' in helper and 'i<=3' in helper
    assert all(helper.count(name+'==14')==1 for name in (
      'value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()'))
    life=run.TEST_SOURCE_OVERRIDES['ApiProcessLifetimeTest'].read_text()
    selected=re.findall(r'(?ms)^  @Test\n  void lifeBudget\d{3}\(.*?^  }',life)
    assert len(selected)==10
    assert all(not any(token in body for token in ('.install(', 'HookDriver','ProcessBuilder','Runtime.getRuntime')) for body in selected)
    ordinary=run.TEST_SOURCE_OVERRIDES['WebLifetimeOrdinaryCloseTest'].read_text()
    assert ordinary.count('@Test')==3 and set(re.findall(r'void (wlClose\d{3})',ordinary))=={'wlClose001','wlClose002','wlClose003'}
    assert all(token not in ordinary for token in ('.install(','.main(','ProcessBuilder','Runtime.getRuntime','Thread.sleep'))
    run.main()
