"""Actual new Batch full12 plus necessary old24, own JVM SDK only, no Batch/Morning/native start."""
import re
import scoped_prometheus_host as run
SOURCE='3359b14899beb17538b1408fe6ea63566f818a00'
COMPILE=run.host.W/'pg8910-batch-full-text-static-fixed-six-compile-v1'
COMPILE_SHA='bdc542236d6e176680afeaa1b02a181cb501117b961b48e0e5a5a7bc0a7543a8'
COUNTS={'BatchMetricTextTest':36}
def fixture_contract(text):
    body=''.join(text.split())
    for number in ('002','003'):
        begin=body.index('voidbatchfull'+number)
        end=body.index('@Test',begin)
        method=body[begin:end]
        assert method.index('varstandard=')<method.index('try(varsource=')
        assert method.count('standard.close();')==2 and '}finally{standard.close();}' in method
        assert 'try(varsource=newRegistry(counter(2.5));varstandard=' not in method
        if number=='002':
            assert method.count('assertEquals("",formatter.scrape(source,"STANDARD",standard));')==2
            assert 'assertEquals(0,source.reads.get());' in method and 'assertEquals(0,calls.get());' in method
        else:
            assert method.count('assertThrows(IllegalStateException.class,()->formatter.scrape(source,"DEBUG",standard));')==2
            assert 'assertFalse(source.isClosed());' in method

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg8912-batch-full-text-static-fixed-host-v1'
    run.OUT=run.host.BASE/'PG8912-batch-full-text-static-fixed-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/BatchFullTextJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricTextTest.java'
    run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=()
    run.COUNTS=COUNTS
    run.SESSION_ID='PG8912-BATCH-FULL-TEXT'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])==['dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest']
    text=run.NEW_TEST.read_text()
    for prefix,count in [('batchtext',24),('batchfull',12)]:
        ids=re.findall(r'void\s+('+prefix+r'\d{3})',text)
        assert len(ids)==count and set(ids)=={prefix+str(i).zfill(3) for i in range(1,count+1)}
    fixture_contract(text)
    main=(run.host.ROOT/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricText.java').read_text()
    assert 'private static final String STANDARD_MODE = "STANDARD";' in main
    assert 'if (STANDARD_MODE.equals(mode)) return custom;' in main
    assert 'if ("STANDARD".equals(mode))' not in main
    assert text.count('@Test')==36 and 'org.junit.jupiter.api.Test' in text
    assert run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
