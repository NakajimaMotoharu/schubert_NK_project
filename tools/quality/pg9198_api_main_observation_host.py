"""New APIOBSBOOT8 static factory/release only; no Main object/startup/provider pool."""
import re
import scoped_prometheus_host as run
SOURCE='9f7a3215621dca09184ea24d0ba824b3a002b329'
COMPILE=run.host.W/'pg9196-api-main-observation-six-compile-v1'
COMPILE_SHA='4e9f7decf57be45c86e742838802c677e1a61ce9f7f0dcb5b7c7e3999b4d7a4d'
COUNTS={'ApiProcessObservationFactoryTest':8}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9198-api-main-observation-host-v1'
    run.OUT=run.host.BASE/'PG9198-api-main-observation-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiMainObservationJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessObservationFactoryTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=()
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9198-API-MAIN-OBSERVATION'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.bootstrap.ApiProcessObservationFactoryTest']
    cases=re.findall(r'void\s+(apiObsBoot\d{3})',run.NEW_TEST.read_text())
    assert len(cases)==8 and set(cases)=={'apiObsBoot'+str(i).zfill(3) for i in range(1,9)} and run.NEW_TEST.read_text().count('@Test')==8
    compact=''.join(run.HELPER.read_text().split())
    checks=('value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()')
    counts=[compact.count(name+'==8') for name in checks]
    assert counts==[1]*4 and sum(COUNTS.values())==8
    body=run.NEW_TEST.read_text()
    for forbidden in ('new ApiProcessMain(','.main(','.run(','.install(', 'HookDriver','ProcessBuilder'):
        assert forbidden not in body
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
