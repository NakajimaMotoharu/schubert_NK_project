"""Exact50 source deltas and41 added physical, current30 only actually qualified."""
import pg7160_filesystem_health_trace as trace

if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7232-db-pool-trace-v1'
    trace.SOURCE='e9c0ba2a180262f8410ae16c46f5909787b5132b'
    trace.SOURCE_COUNT=50;trace.PREVIOUS_COUNT=48;trace.CURRENT_TESTS=132;trace.CURRENT_SUITES=18
    trace.CURRENT_EXECUTABLE=30;trace.ADDED_PHYSICAL=41;trace.REPORTS=(1604,1605)
    trace.NEW_SPEC=1603;trace.NEW_TEST_IDS='DBTIME001..008'
    trace.ALLOWED_NEW_NAMES={'TimedDbPoolMonitor.java','TimedDbPoolMonitorTest.java'}
    trace.EDITED_EXISTING=set();trace.EXTRA_SPECS={};trace.EXTRA_TEST_IDS={}
    trace.PINS['physical']=('PG7230-db-pool-six-post-v1/manifest.json','4d3d8a5dbbac6e21fab22b12799467b8ed9af3c1439eb23a87a7477241015a2a')
    trace.PINS['currentBatch']=('PG7226-db-pool-post-v1/manifest.json','bd2cc87daab25d573fad196fcaff81c2f7d7fa63d8ccfea2ba850779729956d4')
    trace.PINS['previousTrace']=('PG7218-heap-connection-trace-v1/manifest.json','763e8d9e96b4f05e99c8983838fc5c2b5a592d84c50869815407a609690eea71')
    trace.main()
