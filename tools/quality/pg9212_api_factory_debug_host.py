"""Only new factory positive fake-supply method; supporting fixtures compile but are not selected."""
import re
import scoped_prometheus_host as run

SOURCE='3641d0f49e6b33fe64de718703f134406dfddb30'
COMPILE=run.host.W/'pg9210-api-factory-debug-six-compile-v1'
COMPILE_SHA='80b8d4f5f4e16723b5871771fcd3bd03bd068e2a59d17cbf1e8d6e8486f3a39b'
COUNTS={'ApiProcessObservationFactoryTest':1}

if __name__=='__main__':
    run.SOURCE=SOURCE; run.COMPILE=COMPILE; run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9212-api-factory-debug-host-v1'
    run.OUT=run.host.BASE/'PG9212-api-factory-debug-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiFactoryDebugJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessObservationFactoryTest.java'
    support=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring'
    run.EXTRA_TEST_SOURCES=tuple(support/name for name in (
      'ApiFactoryObservationFixture.java','ApiReadOnlyObservationAttemptTest.java',
      'OutboxObservationRepositoryTest.java','DbPoolMetricObservationTest.java'))
    run.TEST_SOURCE_OVERRIDES={}; run.COUNTS=COUNTS
    run.SESSION_ID='PG9212-API-FACTORY-DEBUG'; run.FIXTURES={}
    helper=''.join(run.HELPER.read_text().split())
    assert '.selectors(DiscoverySelectors.selectMethod(types.getFirst(),"apiObsBoot009"))' in helper
    assert 'selectClass' not in helper and re.findall(r'DiscoverySelectors.selectMethod\(',helper)==['DiscoverySelectors.selectMethod(']
    assert all(helper.count(name+'==1')==1 for name in (
      'value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()'))
    text=run.NEW_TEST.read_text()
    assert len(re.findall(r'(?m)^  @Test$',text))==9
    assert set(re.findall(r'void (apiObsBoot\d{3})',text))=={'apiObsBoot'+str(i).zfill(3) for i in range(1,10)}
    assert all(word not in text for word in ('new ApiProcessMain(','.main(','.run(','.install(','HookDriver','ProcessBuilder'))
    fixture=(support/'ApiFactoryObservationFixture.java').read_text()
    assert 'System.getProperty("hikaricp.configurationFile")' in fixture and 'return new ApiFactoryObservationFixture();' in fixture
    assert 'super.getConnection' not in fixture and 'new HikariConfig' not in fixture
    run.main()
