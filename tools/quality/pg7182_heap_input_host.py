"""Current100 pure monitoring PT, owned MXBean/clock/FileStore only; no management or target access."""
import pg7006_monitoring_pure_host as runner
import pg7166_observation_clock_host as previous

SLOT=runner.host.W/'pg7182-heap-input-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.JvmHeapHealthObservationTest')


if __name__=='__main__':runner.main(SLOT,SUITES)
