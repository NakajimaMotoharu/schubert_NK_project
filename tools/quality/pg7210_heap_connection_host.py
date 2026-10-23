"""Changed shared poller and heap connection: genuine124 fixture-only PT, no live providers."""
import pg7006_monitoring_pure_host as runner
import pg7196_timed_heap_host as previous

SLOT=runner.host.W/'pg7210-heap-connection-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.MonitoringPollerTest',
        'dev.codex.schubert.nk.batch.monitoring.JvmHeapHealthMonitorTest')

if __name__=='__main__':runner.main(SLOT,SUITES)
