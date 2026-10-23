"""Current108/all44 source/37 physical, no prior-source edits or coverage union."""
import pg7160_filesystem_health_trace as trace


if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7204-timed-heap-trace-v1'
    trace.SOURCE='41905e2f089eec0aeea8c8f0acca9cc657814a00'
    trace.SOURCE_COUNT=44;trace.PREVIOUS_COUNT=42;trace.CURRENT_TESTS=108;trace.CURRENT_SUITES=15
    trace.CURRENT_EXECUTABLE=26;trace.ADDED_PHYSICAL=37;trace.REPORTS=(1596,1597)
    trace.NEW_SPEC=1595;trace.NEW_TEST_IDS='HEAPTIME001..008'
    trace.ALLOWED_NEW_NAMES={'TimedJvmHeapMonitor.java','TimedJvmHeapMonitorTest.java'}
    trace.EDITED_EXISTING=set();trace.EXTRA_SPECS={};trace.EXTRA_TEST_IDS={}
    trace.PINS['physical']=('PG7202-timed-heap-six-post-v1/manifest.json','5c1b8abcad3f66926675e1c41951b95197643fcbb5d0b44888797677e6027b32')
    trace.PINS['currentBatch']=('PG7198-timed-heap-post-v1/manifest.json','e0186e220a22556c0706b55513f287924e6326bd75699fd19a5bca85cfa0a6be')
    trace.PINS['previousTrace']=('PG7191-heap-input-trace-v2/manifest.json','06588f80a3e0ade520c2af93f9a39b9b6f1767d885038195e0c072ebda482291')
    trace.main()
