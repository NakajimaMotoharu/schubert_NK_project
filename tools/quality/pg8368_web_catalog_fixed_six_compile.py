"""BUG1700 catalog literal repair; new normal six/source snapshot, no prior success transfer."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = 'e5f0ae543177ccd5f399e58d8588092868466f8e'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8368-web-catalog-fixed-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8368-web-catalog-fixed-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
