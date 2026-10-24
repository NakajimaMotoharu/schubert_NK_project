"""New role-local owned standard source32/2 original own JVM, exact import/selection guard."""
import json
import scoped_prometheus_host as run

SOURCE='4c97764a913a09fd39d9881eb6e112e66c1547e3'
COMPILE=run.host.W/'pg8710-web-batch-standard-source-fixed-six-compile-v1'
COMPILE_SHA='d4e08af5550e1da687757e2279f3f4faca6192b50a4de3d7a3efc6dd1d70d374'
COUNTS={'WebStandardMetricSourceTest':16,'BatchStandardMetricSourceTest':16}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8712-web-batch-standard-source-host-v1'
    run.OUT=run.host.BASE/'PG8712-web-batch-standard-source-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/WebBatchStandardMetricSourceJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebStandardMetricSourceTest.java'
    run.TEST_SOURCE_OVERRIDES={'BatchStandardMetricSourceTest':run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchStandardMetricSourceTest.java'}
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8712-WEB-BATCH-STANDARD-SOURCE'
    run.FIXTURES={}
    path=run.host.BASE/'PG8705-web-batch-external-import-preflight-v1/manifest.json'
    assert run.host.sha(path)=='fac825aca5eb0b8359327b48d248a536a186e53157233761dfd2ff66d05fa7df'
    guard=json.loads(path.read_text())
    assert guard['source']==SOURCE and guard['actualExit']==0 and len(guard['negativeGuards'])==12 and guard['helperSha256']==run.host.sha(run.HELPER)
    assert all(run.host.sha(run.host.ROOT/row['path'])==row['sha256'] for row in guard['sourceRows'])
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
