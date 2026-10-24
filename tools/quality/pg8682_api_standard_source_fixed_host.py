"""New APIHOST16 own fresh JVM against fixed normal six source, no runtime target."""
import re
import scoped_prometheus_host as run

SOURCE='6f6c5c384b3e7f2ffe79cc5472ed86894c59f7ea'
COMPILE=run.host.W/'pg8680-api-standard-source-fixed-six-compile-v1'
COMPILE_SHA='759fa9eec692961e439ac48b76118ba1cc6f8b42b24d03a44d51f76e9f6cfdb7'
COUNTS={'ApiStandardMetricSourceTest':16}

if __name__ == '__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8682-api-standard-source-fixed-host-v1'
    run.OUT=run.host.BASE/'PG8682-api-standard-source-fixed-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiStandardMetricSourceJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSourceTest.java'
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8682-API-STANDARD-SOURCE'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSourceTest']
    assert run.SLOT.name=='pg8682-api-standard-source-fixed-host-v1' and run.OUT.name=='PG8682-api-standard-source-fixed-host-v1'
    run.main()
