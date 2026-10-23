"""Same-source54 pure monitoring tests; no live observations or runtime operations."""
import pg7006_monitoring_pure_host as runner
import pg7026_monitoring_pipeline_host as pipeline

SLOT = runner.host.W/'pg7044-monitoring-status-host-v1'
SUITES = (*pipeline.SUITES, 'dev.codex.schubert.nk.batch.monitoring.MonitoringStatusTextTest')


if __name__ == '__main__':
    runner.main(SLOT, SUITES)
