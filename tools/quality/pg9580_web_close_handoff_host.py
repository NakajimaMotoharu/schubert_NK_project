"""Necessary changed-close regression: one uninstalled finite owner, no native test selection."""
import scoped_prometheus_host as run

SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
METHOD='life002ForeignHookWaitsForActualOwnerNotificationAndPreservesInterrupt'
COUNTS={'WebProcessLifetimeTest':1}

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=run.host.W/'pg9246-web-life-lock-six-compile-v1'
    run.COMPILE_SHA='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    run.SLOT=run.host.W/'pg9580-web-close-handoff-host-v1';run.OUT=run.host.BASE/'PG9580-web-close-handoff-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/WebCloseHandoffJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebProcessLifetimeTest.java'
    probe=run.host.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/CallerMonitorProbe.java'
    run.TEST_SOURCE_OVERRIDES={};run.EXTRA_TEST_SOURCES=(probe,);run.COUNTS=COUNTS
    run.SESSION_ID='PG9580-WEB-CLOSE-HANDOFF';run.FIXTURES={}
    assert run.host.sha(run.NEW_TEST)=='c9cbb3629a84c507d7da7df3484aa0cf5807664400c38439ec5e1f6edbbb324b'
    assert run.host.sha(probe)=='e502853332c70415707eb38f8aa52e0096f54c4a106c21a51d23cb47cbbda9fd'
    helper=''.join(run.HELPER.read_text().split())
    assert 'DiscoverySelectors.selectMethod(TYPE,METHOD)' in helper and 'selectClass' not in helper
    assert '"'+METHOD+'"' in helper
    source=run.NEW_TEST.read_text();method=source.split('  void '+METHOD+'() throws Exception {',1)[1].split('  @Test',1)[0]
    assert method.count('lifetime.shutdown()')==1 and method.count('lifetime.close()')==2
    assert all(x not in method for x in ('.install(','.main(','.run(','ProcessBuilder','Runtime.getRuntime','retainUnknown','holdUnknownInterval'))
    run.main()
