"""Source without deprecated timestamp APIs; full normal six build, no PT PASS claim."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'cd81f37f0527177b5f790a1cb1a5e519ba714561'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8256-summary-encoder-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8256-summary-encoder-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
