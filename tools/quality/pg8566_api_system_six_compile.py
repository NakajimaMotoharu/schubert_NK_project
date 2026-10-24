"""New API standard CPU-FD source, normal six compile; PT0 UNRUN."""
import pg8504_web_batch_jvm_six_compile as template

if __name__ == '__main__':
    stage = template.previous.stage
    stage.SOURCE = 'e027929a7a6da504e0d03efd517ea98656ce369b'
    stage.SLOT = stage.host.W / 'pg8566-api-system-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8566-api-system-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**template.previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in template.previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if template.previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
