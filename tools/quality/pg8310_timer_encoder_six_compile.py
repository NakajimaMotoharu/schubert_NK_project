"""Explicit Timer seconds output source normal six build, no product test execution."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '1a066d08bf709e6a883fce1d289f9ce081d3bf54'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8310-timer-encoder-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8310-timer-encoder-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
