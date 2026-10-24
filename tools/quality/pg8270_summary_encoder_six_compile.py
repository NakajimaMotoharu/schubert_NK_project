"""BUG1695 exact compare correction: new normal six build, PT0/UNRUN."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '7cba540ba7213e390d21ff46db73420caa5056e4'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8270-summary-encoder-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8270-summary-encoder-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
