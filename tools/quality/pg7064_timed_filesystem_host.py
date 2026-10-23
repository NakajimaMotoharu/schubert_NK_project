"""Same-source70 pure monitoring tests, no actual filesystem or collector operation."""
import pg7006_monitoring_pure_host as runner
import pg7056_monitoring_window_host as window

SLOT=runner.host.W/'pg7064-timed-filesystem-host-v1'
PREFIX='dev.codex.schubert.nk.batch.monitoring.'
SUITES=(*window.SUITES,PREFIX+'AlertContinuityTest',PREFIX+'TimedFilesystemMonitorTest')


if __name__=='__main__':
    runner.main(SLOT,SUITES)
