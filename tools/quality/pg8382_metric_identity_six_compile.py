"""BUG1701 four exporter name snapshots normal six build, no old source PT transfer."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'f775f095c0721340c20376b8d37d8baa2e97bc21'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8382-metric-identity-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8382-metric-identity-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
