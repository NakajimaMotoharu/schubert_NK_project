"""New API standard CPU-FD source, normal six compile; PT0 UNRUN."""
import pg8504_web_batch_jvm_six_compile as template

if __name__ == '__main__':
    stage = template.previous.stage
    stage.SOURCE = 'e81adb96849e4067beb12f212350ab4fbd4b1998'
    stage.SLOT = stage.host.W / 'pg8608-web-batch-standard-assembly-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8608-web-batch-standard-assembly-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**template.previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in template.previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if template.previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
