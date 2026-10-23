"""All48 sources/39 physical additions, current28 distinct from historical Web."""
import pg7160_filesystem_health_trace as trace

if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7218-heap-connection-trace-v1'
    trace.SOURCE='0b8aa6dab9b91d378811b0bda24d6a61bbc73106'
    trace.SOURCE_COUNT=48;trace.PREVIOUS_COUNT=44;trace.CURRENT_TESTS=124;trace.CURRENT_SUITES=17
    trace.CURRENT_EXECUTABLE=28;trace.ADDED_PHYSICAL=39;trace.REPORTS=(1600,1601)
    trace.NEW_SPEC=1599;trace.NEW_TEST_IDS='POLL001..008/HEAPCONN001..008'
    trace.ALLOWED_NEW_NAMES={'MonitoringPoller.java','MonitoringPollerTest.java',
                            'JvmHeapHealthMonitor.java','JvmHeapHealthMonitorTest.java'}
    prefix='src/schubert-nk-batch/src/'
    main=prefix+'main/java/dev/codex/schubert/nk/batch/monitoring/'
    tests=prefix+'test/java/dev/codex/schubert/nk/batch/monitoring/'
    trace.EDITED_EXISTING={main+'FilesystemHealthMonitor.java',tests+'JvmHeapHealthObservationTest.java',
                           tests+'MonitoringObservationClockTest.java'}
    trace.EXTRA_SPECS={path:[1599] for path in trace.EDITED_EXISTING}
    trace.EXTRA_TEST_IDS={path:'POLL001..008/HEAPCONN001..008' for path in trace.EDITED_EXISTING}
    trace.PINS['physical']=('PG7216-heap-connection-six-post-v1/manifest.json','687a7487c535c1a954614582da4e78298fea36608dabaac54920dc7c71e6ea2e')
    trace.PINS['currentBatch']=('PG7212-heap-connection-post-v1/manifest.json','f42c119d34dbe54c5c22f8f75f0d1b1eab80f20b648c419c4ba9d6138e50aa58')
    trace.PINS['previousTrace']=('PG7204-timed-heap-trace-v1/manifest.json','79b1052ccafe79754ab4178702b7a4ef302ba670fd4c9ba05a3fe7ff818139a7')
    trace.main()
