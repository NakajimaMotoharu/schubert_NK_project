"""Actual borrowed Micrometer provider15 tests, exact complete runtime dependency pins, no target IO."""
import pg7006_monitoring_pure_host as runner

SLOT=runner.host.W/'pg7106-micrometer-http-host-v1'
POM='tools/quality/harnesses/monitoring-web-http-pom.xml'
SUITES=('dev.codex.schubert.nk.web.monitoring.HttpMetricContractTest',
        'dev.codex.schubert.nk.web.monitoring.HttpMetricRecorderTest')
REPO=runner.host.TC/'m2/repository'
SDK={str(REPO/path):digest for path,digest in (
 ('io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar','9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'),
 ('io/micrometer/micrometer-commons/1.17.1/micrometer-commons-1.17.1.jar','f2cee6ef046e72eec8128474c7f58c6217173b45ae373c30de0289f2a56ab0fd'),
 ('io/micrometer/micrometer-observation/1.17.1/micrometer-observation-1.17.1.jar','eb34f0cd84a879393ae5c21160fc06385ccdc74f36a4d1e31b199f59acfdaf71'),
 ('org/hdrhistogram/HdrHistogram/2.2.2/HdrHistogram-2.2.2.jar','22d1d4316c4ec13a68b559e98c8256d69071593731da96136640f864fa14fad8'))}


if __name__=='__main__':
    runner.POM=POM
    runner.DEPENDENCY_JARS=SDK
    runner.main(SLOT,SUITES)
