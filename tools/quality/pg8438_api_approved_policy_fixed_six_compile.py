"""New API approved policy source normal six/null/format build; product PT0 UNRUN."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '75a198d53081b2a70babc9f2497d4faddfdbd508'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8438-api-approved-policy-fixed-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8438-api-approved-policy-fixed-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()



