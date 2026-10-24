"""Web counter/shared Web text source, normal six compile/NullAway, product PT0."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '30fe7bb8947cc8c5c1ac56838c4af4197afcc9df'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8334-web-counter-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8334-web-counter-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
