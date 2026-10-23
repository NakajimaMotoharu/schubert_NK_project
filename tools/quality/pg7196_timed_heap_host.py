"""Actual108 pure monitoring PT, supplied heap reports/values, no real memory or process operation."""
import pg7006_monitoring_pure_host as runner
import pg7182_heap_input_host as previous

SLOT=runner.host.W/'pg7196-timed-heap-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.TimedJvmHeapMonitorTest')


if __name__=='__main__':runner.main(SLOT,SUITES)
