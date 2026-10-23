"""Fixed-source59 deltas/51 added physical, current40 vs historical Web/compile descriptors."""
import pg7160_filesystem_health_trace as trace

if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7280-transfer-metric-trace-v2'
    trace.SOURCE='1470b0ea110bcf9598bcdc423745b812b580f9ad'
    trace.SOURCE_COUNT=59;trace.PREVIOUS_COUNT=57;trace.CURRENT_TESTS=161;trace.CURRENT_SUITES=22
    trace.CURRENT_EXECUTABLE=40;trace.ADDED_PHYSICAL=51;trace.REPORTS=(1616,1617)
    trace.NEW_SPEC=1615;trace.NEW_TEST_IDS='TRANSFERMET001..008';trace.NEW_SS='341,351'
    trace.ALLOWED_NEW_NAMES={'TransferMetricRecorder.java','TransferMetricRecorderTest.java'}
    trace.EDITED_EXISTING=set();trace.EXTRA_SPECS={};trace.EXTRA_TEST_IDS={}
    trace.PINS['physical']=('PG7278-transfer-metric-six-post-v2/manifest.json','f5941f082d691d71f33e1315c52012afdac7011f6763220fb3a60b21a64a2c3b')
    trace.PINS['currentBatch']=('PG7274-transfer-metric-post-v2/manifest.json','f167da99fa7062a2d890cd451dc99882b4ff553f1b041aec6b2087c7e4d6f876')
    trace.PINS['previousTrace']=('PG7260-batch-metric-trace-v1/manifest.json','90ad5b48b1fd626d4e52dc103e90bd551a07248764b8f2d4a82e581815d1674b')
    trace.main()
