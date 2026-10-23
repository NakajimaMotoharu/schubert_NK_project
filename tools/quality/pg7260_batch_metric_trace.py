"""Exact57 source deltas/47 added physical, current36 and compile-only POMs distinct."""
import pg7160_filesystem_health_trace as trace

if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7260-batch-metric-trace-v1'
    trace.SOURCE='34813cef90b2a5c6b2ad3be835565bf53e96a875'
    trace.SOURCE_COUNT=57;trace.PREVIOUS_COUNT=52;trace.CURRENT_TESTS=153;trace.CURRENT_SUITES=21
    trace.CURRENT_EXECUTABLE=36;trace.ADDED_PHYSICAL=47;trace.REPORTS=(1612,1613)
    trace.NEW_SPEC=1611;trace.NEW_TEST_IDS='BATCHMET001..005/BATCHREC001..008';trace.NEW_SS='341,351'
    trace.ALLOWED_NEW_NAMES={'BatchMetricContract.java','BatchMetricContractTest.java',
      'BatchMetricRecorder.java','BatchMetricRecorderTest.java','pom.xml'}
    trace.EDITED_EXISTING=set();trace.EXTRA_SPECS={};trace.EXTRA_TEST_IDS={}
    trace.PINS['physical']=('PG7258-batch-metric-six-post-v1/manifest.json','8546601af65ecfb0de5e57f460349651bcfc6ab8a242ee9b9725b3c87d283866')
    trace.PINS['currentBatch']=('PG7254-batch-metric-post-v1/manifest.json','379cef1807e526b900bd9ff61c1fd96224bad8be09e355862133adad7f34bc9a')
    trace.PINS['previousTrace']=('PG7246-sync-p95-trace-v1/manifest.json','6422d1e9859fe7a5ddd8ac4ca3c4f21ffec9d0aa7a68e5b0b5738b275d294d02')
    trace.main()
