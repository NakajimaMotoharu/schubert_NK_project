"""New Web Gauge source, normal six warning/null/format gates; PT0 UNRUN."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'e1ba2ccc51f1f24bd48d74e3b906b48489473a39'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8350-web-gauge-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8350-web-gauge-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
