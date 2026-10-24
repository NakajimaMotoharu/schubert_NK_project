"""New OBSOWN18 own JVM/fake observation only; supporting fixture outers are compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='ecfcbf9f6ab81f77301833eda3fba464c72eb4b5'
COMPILE=run.host.W/'pg9168-api-stop-budget-six-compile-v1'
COMPILE_SHA='557028d74e26b39a1fa33469e7950419d5e6c3c8b7e04f5479ecb9c1eb8df61c'
COUNTS={'ApiStopBudgetTest':18}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9170-api-stop-budget-host-v1'
    run.OUT=run.host.BASE/'PG9170-api-stop-budget-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiStopBudgetJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudgetTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=()
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9170-API-STOP-BUDGET'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.bootstrap.ApiStopBudgetTest']
    cases=re.findall(r'void\s+(apiStop\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==18 and set(cases)=={'apiStop'+str(i).zfill(3) for i in range(1,19)} and run.NEW_TEST.read_text().count('@Test')==18
    compact=''.join(run.HELPER.read_text().split())
    checks=('value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()')
    counts=[compact.count(name+'==18') for name in checks]
    assert counts==[1]*4 and sum(COUNTS.values())==18
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
