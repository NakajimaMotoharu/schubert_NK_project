"""Only four uninstalled Web owner methods; no legacy HookDriver or UNKNOWN intervals selected."""
import re
import scoped_prometheus_host as run

SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
COMPILE=run.host.W/'pg9246-web-life-lock-six-compile-v1'
COMPILE_SHA='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
COUNTS={'WebLifetimeOrdinaryCloseTest':4}

if __name__=='__main__':
    run.SOURCE=SOURCE; run.COMPILE=COMPILE; run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9248-web-life-lock-host-v1'; run.OUT=run.host.BASE/'PG9248-web-life-lock-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/WebLifeLockJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebLifetimeOrdinaryCloseTest.java'
    run.TEST_SOURCE_OVERRIDES={}; run.EXTRA_TEST_SOURCES=(); run.COUNTS=COUNTS
    run.SESSION_ID='PG9248-WEB-LIFE-LOCK'; run.FIXTURES={}
    helper=''.join(run.HELPER.read_text().split())
    assert 'List.of("dev.codex.schubert.nk.web.bootstrap.WebLifetimeOrdinaryCloseTest")' in helper
    assert all(helper.count(name+'==4')==1 for name in (
      'value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()'))
    source=run.NEW_TEST.read_text()
    assert source.count('@Test')==4 and set(re.findall(r'void (wlClose\d{3})',source))=={'wlClose'+str(i).zfill(3) for i in range(1,5)}
    assert not any(token in source for token in ('.install(','.main(','ProcessBuilder','Runtime.getRuntime','retainUnknown','holdUnknownInterval'))
    run.main()
