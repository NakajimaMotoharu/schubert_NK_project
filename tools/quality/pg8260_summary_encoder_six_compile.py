"""Fresh current fixture and warning-clean Main normal six build; test execution forbidden."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'b978c6832fe07ec65c162ab90d8bfe0bbddb8034'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8260-summary-encoder-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8260-summary-encoder-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
