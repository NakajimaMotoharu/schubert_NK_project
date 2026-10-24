"""New Batch closed text source normal six/null/format build; product PT0 UNRUN."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '441158e6eda607cb2cb24a192d73555740cb27a9'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8462-batch-text-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8462-batch-text-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()





