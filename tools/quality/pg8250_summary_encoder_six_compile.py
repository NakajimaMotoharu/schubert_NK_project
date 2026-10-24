"""New warning-clean builder source normal six package/NullAway, no PT."""
import pg8242_summary_encoder_six_compile as previous

SOURCE = '04d35bf9bcf2865aabcde1539f8a4ad281fd461d'

if __name__ == '__main__':
    stage = previous.stage
    stage.SOURCE = SOURCE
    stage.SLOT = stage.host.W / 'pg8250-summary-encoder-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG8250-summary-encoder-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    stage.DEPENDENCY_JARS = {**previous.sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in previous.json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())['entries'] if previous.Path(row['path']).suffix == '.jar'}}
    stage.main()
