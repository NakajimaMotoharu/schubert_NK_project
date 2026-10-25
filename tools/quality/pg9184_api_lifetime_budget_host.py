"""New OBSOWN18 own JVM/fake observation only; supporting fixture outers are compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='6c271f74da3e09cbcf52e6c2abf5dd27fe93acd5'
COMPILE=run.host.W/'pg9182-api-lifetime-budget-six-compile-v2'
COMPILE_SHA='dc1a8a844dafbed01e8b9beb1123221448ab7e09593b9114efcf98c05e8e057b'
COUNTS={'ApiProcessLifetimeTest':10}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9184-api-lifetime-budget-host-v1'
    run.OUT=run.host.BASE/'PG9184-api-lifetime-budget-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiLifetimeBudgetJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetimeTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=()
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9184-API-LIFETIME-BUDGET'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.bootstrap.ApiProcessLifetimeTest']
    cases=re.findall(r'void\s+(lifeBudget\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==10 and set(cases)=={'lifeBudget'+str(i).zfill(3) for i in range(1,11)}
    compact=''.join(run.HELPER.read_text().split())
    checks=('value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()')
    counts=[compact.count(name+'==10') for name in checks]
    assert counts==[1]*4 and sum(COUNTS.values())==10
    helper=run.HELPER.read_text()
    assert 'DiscoverySelectors::selectClass' not in helper and 'DiscoverySelectors.selectClass' not in helper
    assert 'IntStream.rangeClosed(1,10)' in compact and 'DiscoverySelectors.selectMethod(types.getFirst(),"lifeBudget"' in compact
    bodies=re.findall(r'(?ms)^  @Test\n  void lifeBudget\d{3}\(.*?^  }',run.NEW_TEST.read_text())
    assert len(bodies)==10
    for body in bodies:
        assert not any(word in body for word in ('install(', 'HookDriver','ProcessBuilder','Runtime.getRuntime'))
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
