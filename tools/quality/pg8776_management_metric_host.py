"""Exact new HTTP boundary32/2 ordinary own JVM, no native/service startup."""
import re
import scoped_prometheus_host as run

SOURCE='fde3baa14040def7ed3736576114f05ca2d60cbd'
COMPILE=run.host.W/'pg8774-management-metric-six-compile-v1'
COMPILE_SHA='PENDING_NORMAL_HASH'
COUNTS={'ApiMetricHttpHandlerTest':18,'WebMetricHttpHandlerTest':18}

def fixture_contract(body,role):
    assert 'new '+role.title()+'MetricContext<String>(' in body and 'throw new AssertionError("STD setup")' in body
    assert 'Gauge.builder("nk_db_pool_connections", value, state -> state[0])' in body
    assert '.tags("service", "'+role.upper()+'", "state", "active")' in body
    assert 'nk_metric_http_fixture' not in body
    for value in ('7.5','9.5'):
        assert 'nk_db_pool_connections{service=\\"'+role.upper()+'\\",state=\\"active\\"} '+value+'\\n' in body
    assert 'org.junit.jupiter.api.Test' in body and 'org.junit.jupiter.'+role+'.Test' not in body if role!='api' else 'org.junit.jupiter.api.Test' in body

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8776-management-metric-host-v1'
    run.OUT=run.host.BASE/'PG8776-management-metric-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ManagementMetricJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandlerTest.java'
    web=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricHttpHandlerTest.java'
    run.TEST_SOURCE_OVERRIDES={'WebMetricHttpHandlerTest':web}
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8776-MANAGEMENT-METRIC'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1
    actual=re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])
    assert len(actual)==2 and set(actual)=={'dev.codex.schubert.nk.'+role+'.monitoring.'+title+'MetricHttpHandlerTest' for role,title in (('api','Api'),('web','Web'))}
    for role,path in (('api',run.NEW_TEST),('web',web)):
        body=path.read_text()
        cases=re.findall(r'void\s+('+role+r'mhttp\d{3})',body)
        assert len(cases)==18 and set(cases)=={role+'mhttp'+str(i).zfill(3) for i in range(1,19)}
        assert body.count('@Test')==18 and 'org.junit.jupiter.api.Test' in body
        fixture_contract(body,role)
        for changed in (body.replace('MetricContext<String>(', 'MetricContext<>('),body.replace('nk_db_pool_connections','nk_metric_http_fixture'),body.replace('"state", "active"','"state", "idle"')):
            assert changed!=body
            try: fixture_contract(changed,role)
            except AssertionError: pass
            else: raise AssertionError('every fixture mutation rejects')
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
