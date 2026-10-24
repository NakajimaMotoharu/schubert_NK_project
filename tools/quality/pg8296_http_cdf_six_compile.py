"""BUG1696 explicit state-lock helper source normal six build; original outcomes retained."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'f02fae44edbcf7abba214a6507935c15ae5f9ee9'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8296-http-cdf-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8296-http-cdf-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
