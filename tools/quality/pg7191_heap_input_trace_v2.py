"""Corrected immediate previous-source edit anchors for all42 rows; no PT or source replay."""
import pg7160_filesystem_health_trace as trace


if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7191-heap-input-trace-v2'
    trace.SOURCE='dc46262abceaac42085a813d872f25669700a096'
    trace.SOURCE_COUNT=42;trace.PREVIOUS_COUNT=39;trace.CURRENT_TESTS=100;trace.CURRENT_SUITES=14
    trace.CURRENT_EXECUTABLE=24;trace.ADDED_PHYSICAL=35;trace.REPORTS=(1592,1593)
    trace.NEW_SPEC=1591;trace.NEW_TEST_IDS='HEAPINPUT001..009'
    trace.ALLOWED_NEW_NAMES={'HealthUsageRatio.java','JvmHeapHealthObservation.java','JvmHeapHealthObservationTest.java'}
    root='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/'
    source=root+'FilesystemHealthObservation.java';ratio=root+'HealthUsageRatio.java'
    trace.EDITED_EXISTING={source}
    trace.EXTRA_SPECS={source:[1591],ratio:[1582]};trace.EXTRA_TEST_IDS={ratio:'FSINPUT001..007'}
    trace.PINS['physical']=('PG7188-heap-input-six-post-v1/manifest.json','78c3cb12d7a708a520bccd6d3e3c142a14c61647765906db0e73172dbf3a1519')
    trace.PINS['currentBatch']=('PG7184-heap-input-post-v1/manifest.json','886b6965fb80bf30cbe964d7858b7687e8a40987ab076ff673d2a5802a727009')
    trace.PINS['previousTrace']=('PG7174-observation-clock-trace-v1/manifest.json','b0a847a40ca446eb3b77e018c46c7767063834a551596fceef7a97a392bf5d6c')
    trace.main()
