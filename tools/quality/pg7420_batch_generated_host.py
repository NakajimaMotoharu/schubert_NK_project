"""Changed-source Batch169+seven generated value contracts, public pure fixtures only."""
import pg7006_monitoring_pure_host as runner
import pg7286_transfer_health_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7420-batch-generated-host-v1'
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.batch.monitoring.GeneratedBatchValueContractTest')

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
