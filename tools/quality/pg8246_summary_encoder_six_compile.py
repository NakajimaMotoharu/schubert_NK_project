"""Fresh six compile after resolving Maven imported descriptors; old failed receipt retained."""
import pg8242_summary_encoder_six_compile as previous

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = previous.SOURCE
    stage.SLOT = stage.host.W / 'pg8246-summary-encoder-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8246-summary-encoder-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
