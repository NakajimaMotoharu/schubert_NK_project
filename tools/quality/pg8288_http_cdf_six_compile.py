"""BUG1696 lifetime-CDF repair normal six build; PT0 explicitly unrun."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'f1a898b58a893837582b06861b33863407792139'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8288-http-cdf-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8288-http-cdf-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
