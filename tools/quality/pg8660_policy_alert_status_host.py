"""New supplied threshold->alert->status actual connection4; no source changes or live observations."""
import re
import scoped_prometheus_host as run

SOURCE = 'f817b004781e6c32aa2d384dd12855cad7175ddc'
COMPILE = run.host.W / 'pg8632-api-web-custom-payload-six-compile-v1'
COMPILE_SHA = '8039af9b7750d5b689c4663cdb6f02634ad857ed76ad52f6f7d3bba25c0d1c9b'
COUNTS = {'PolicyAlertStatusConnectionTest':4}

if __name__ == '__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8660-policy-alert-status-host-v1'
    run.OUT=run.host.BASE/'PG8660-policy-alert-status-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/PolicyAlertStatusJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'tools/quality/architecture/PolicyAlertStatusConnectionTest.java'
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8660-POLICY-ALERT-STATUS'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.batch.monitoring.PolicyAlertStatusConnectionTest']
    assert run.SLOT.name=='pg8660-policy-alert-status-host-v1' and run.OUT.name=='PG8660-policy-alert-status-host-v1'
    run.main()
