"""Changed renderer exact50/2: new24 connection plus necessary26 byte-compatible regressions."""
import re
import scoped_prometheus_host as run

SOURCE='3613b2742c8bcda85a2ec889d023307fadf1875c'
COMPILE=run.host.W/'pg8722-full-metric-payload-six-compile-v1'
COMPILE_SHA='2cb763db0522c0bcc083c86585505d8dbec51e19700b7019c55548ca03a4c63e'
COUNTS={'ApiCustomMetricPayloadTest':25,'WebCustomMetricPayloadTest':25}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8724-full-metric-payload-host-v1'
    run.OUT=run.host.BASE/'PG8724-full-metric-payload-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/FullMetricPayloadJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiCustomMetricPayloadTest.java'
    web=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebCustomMetricPayloadTest.java'
    run.TEST_SOURCE_OVERRIDES={'WebCustomMetricPayloadTest':web}
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8724-FULL-METRIC-PAYLOAD'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1
    actual=re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])
    assert len(actual)==2 and set(actual)=={'dev.codex.schubert.nk.'+role+'.monitoring.'+title+'CustomMetricPayloadTest' for role,title in (('api','Api'),('web','Web'))}
    for role,path in (('api',run.NEW_TEST),('web',web)):
        body=path.read_text()
        cases=re.findall(r'void\s+('+role+r'(?:pay|full)\d{3})',body)
        assert len(cases)==25 and set(cases)=={role+'pay'+str(i).zfill(3) for i in range(1,14)}|{role+'full'+str(i).zfill(3) for i in range(1,13)}
        assert body.count('@Test')==25 and 'org.junit.jupiter.api.Test' in body
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
