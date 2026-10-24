"""App-specific negative fixtures strengthened; Main/POM unchanged, new full snapshot build."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '3968abacec2052b9e7b803702a3a9231f9209f26'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8320-app-duration-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8320-app-duration-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
