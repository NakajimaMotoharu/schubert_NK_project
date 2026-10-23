"""All39 source/33 physical trace; exact planned health/fixture edits, current91 not historical union."""
import pg7160_filesystem_health_trace as trace


if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7174-observation-clock-trace-v1'
    trace.SOURCE='3b2ef576cf46763d67a9e2914dc547afd2f93ef6'
    trace.SOURCE_COUNT=39;trace.PREVIOUS_COUNT=37;trace.CURRENT_TESTS=91;trace.CURRENT_SUITES=13
    trace.CURRENT_EXECUTABLE=22;trace.ADDED_PHYSICAL=33;trace.REPORTS=(1587,1588)
    trace.NEW_SPEC=1586;trace.NEW_TEST_IDS='OBSCLOCK001..008'
    trace.ALLOWED_NEW_NAMES={'MonitoringObservationClock.java','MonitoringObservationClockTest.java'}
    root='src/schubert-nk-batch/src/'
    main=root+'main/java/dev/codex/schubert/nk/batch/monitoring/FilesystemHealthMonitor.java'
    fixture=root+'test/java/dev/codex/schubert/nk/batch/monitoring/FilesystemHealthObservationTest.java'
    trace.EDITED_EXISTING={main,fixture}
    trace.EXTRA_SPECS={main:[1586]};trace.EXTRA_TEST_IDS={main:'OBSCLOCK008'}
    trace.PINS['physical']=('PG7172-observation-clock-six-post-v1/manifest.json','7ee372ea833bd9ed3eecbda6f47e4c8b6713e1f6630d8e69f4e1f441928f91d4')
    trace.PINS['currentBatch']=('PG7168-observation-clock-post-v1/manifest.json','580abe8ff4eea75f6f2fda9fbd45c787f16b468a2536f16590705734f23bdcc5')
    trace.PINS['previousTrace']=('PG7160-filesystem-health-trace-v1/manifest.json','2d22a8b9269ed8fc3e62df273cdb087914a1a5980386622a5674e4719e6ddb8c')
    trace.main()
