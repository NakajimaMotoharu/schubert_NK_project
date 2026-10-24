"""New APIHOST16 own fresh JVM against fixed normal six source, no runtime target."""
import re
import scoped_prometheus_host as run

SOURCE='6cd77b76b004e77d0360efee8a62e4553bab05e1'
COMPILE=run.host.W/'pg8690-api-standard-source-lock-six-compile-v1'
COMPILE_SHA='b8d281d6662fb915405ac192532d7753abe47a9bf7e53c2a623d217b06a69008'
COUNTS={'ApiStandardMetricSourceTest':16}

if __name__ == '__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8692-api-standard-source-lock-host-v1'
    run.OUT=run.host.BASE/'PG8692-api-standard-source-lock-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiStandardMetricSourceJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSourceTest.java'
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8692-API-STANDARD-SOURCE'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSourceTest']
    assert run.SLOT.name=='pg8692-api-standard-source-lock-host-v1' and run.OUT.name=='PG8692-api-standard-source-lock-host-v1'
    run.main()
