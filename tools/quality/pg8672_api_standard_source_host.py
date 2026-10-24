"""New APIHOST16 own fresh JVM against fixed normal six source, no runtime target."""
import re
import scoped_prometheus_host as run

SOURCE='97b82272c9cd7a9d49e0351fc175d451650795af'
COMPILE=run.host.W/'pg8670-api-standard-source-six-compile-v1'
COMPILE_SHA='a5a3d8a2265c101ff20796ac261c8fad6f78b67663e048a5d53bce7886b0575b'
COUNTS={'ApiStandardMetricSourceTest':16}

if __name__ == '__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8672-api-standard-source-host-v1'
    run.OUT=run.host.BASE/'PG8672-api-standard-source-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiStandardMetricSourceJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSourceTest.java'
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8672-API-STANDARD-SOURCE'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSourceTest']
    assert run.SLOT.name=='pg8672-api-standard-source-host-v1' and run.OUT.name=='PG8672-api-standard-source-host-v1'
    run.main()
