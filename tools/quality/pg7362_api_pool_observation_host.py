"""Actual48 ordinary SDK/fake typed Hikari-interface cases, never a real pool/config/DB/JMX connection."""
import pg7006_monitoring_pure_host as runner
import pg7348_api_pool_metric_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7362-api-pool-observation-host-v1'
POM=previous.POM
SUITES=previous.SUITES+('dev.codex.schubert.nk.api.monitoring.DbPoolMetricObservationTest',
                      'dev.codex.schubert.nk.api.monitoring.DbPoolMetricCollectorTest')
EXTRA={str(sdk.REPO/path):digest for path,digest in (
 ('com/zaxxer/HikariCP/7.1.0/HikariCP-7.1.0.jar','2be45c641b841e81df87292e181f2c203500c5f0e9a1676f135927387f3cf40b'),
 ('org/slf4j/slf4j-api/2.0.18/slf4j-api-2.0.18.jar','44508fd1576500688c790b190acdd16fec4f8c79a3e0b900afd70503cf055f55'))}
DEPENDENCIES={**sdk.SDK,**EXTRA}

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
