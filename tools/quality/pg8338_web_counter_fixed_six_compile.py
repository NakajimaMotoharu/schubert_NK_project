"""BUG1698 fixture source fixed; Main unchanged, new full snapshot compile."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '6c91f378543e9c1cbfa0c8a9dd3115f91cbbdccb'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8338-web-counter-fixed-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8338-web-counter-fixed-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
