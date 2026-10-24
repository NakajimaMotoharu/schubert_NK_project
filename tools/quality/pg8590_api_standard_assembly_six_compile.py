"""New API standard CPU-FD source, normal six compile; PT0 UNRUN."""
import pg8504_web_batch_jvm_six_compile as template

if __name__ == '__main__':
    stage = template.previous.stage
    stage.SOURCE = '86ec58d4f8d11350c01d62a5fab0be8a9f1ba670'
    stage.SLOT = stage.host.W / 'pg8590-api-standard-assembly-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8590-api-standard-assembly-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**template.previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in template.previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if template.previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
