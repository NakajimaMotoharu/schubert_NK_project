"""New Web and Batch standard non-resource JVM source normal six/null/format build; product PT0 UNRUN."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '4950b3daf1632ed9f57c3ca42276532b24204745'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8504-web-batch-jvm-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8504-web-batch-jvm-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()









