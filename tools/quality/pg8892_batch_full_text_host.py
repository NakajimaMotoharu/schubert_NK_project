"""Actual new Batch full12 plus necessary old24, own JVM SDK only, no Batch/Morning/native start."""
import re
import scoped_prometheus_host as run
SOURCE='287eba60232970110a626bc2187cc9fcad2fe27f'
COMPILE=run.host.W/'pg8890-batch-full-text-six-compile-v1'
COMPILE_SHA=run.host.sha(COMPILE/'manifest.safe.json')
COUNTS={'BatchMetricTextTest':36}
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8892-batch-full-text-host-v1'
    run.OUT=run.host.BASE/'PG8892-batch-full-text-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/BatchFullTextJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricTextTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=()
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8892-BATCH-FULL-TEXT'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest']
    text=run.NEW_TEST.read_text()
    for prefix,count in [('batchtext',24),('batchfull',12)]:
        ids=re.findall(r'void\s+('+prefix+r'\d{3})',text)
        assert len(ids)==count and set(ids)=={prefix+str(i).zfill(3) for i in range(1,count+1)}
    assert text.count('@Test')==36 and 'org.junit.jupiter.api.Test' in text
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
