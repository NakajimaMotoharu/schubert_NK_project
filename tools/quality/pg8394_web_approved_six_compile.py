"""Web approved catalog/model join normal six build, PT0 explicitly UNRUN."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'b347581d26d925885a4cb882eeb2326449eded94'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8394-web-approved-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8394-web-approved-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
