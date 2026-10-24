"""BUG1697 corrected app-owned duration adapters; canonical limited bootstrap restored."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'd496e7430d70a9edb4092c2b09ca78b8ecfd9004'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8316-app-duration-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8316-app-duration-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
