"""New summary encoder normal six compile/NullAway, PT0 explicitly UNRUN."""
from pathlib import Path
import json
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE = 'e43932834'
SLOT = stage.host.W / 'pg8242-summary-encoder-six-compile-v1'

if __name__ == '__main__':
    stage.SOURCE = SOURCE
    stage.SLOT = SLOT
    stage.OUT = stage.host.BASE / 'PG8242-summary-encoder-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    coordinates = json.loads((stage.host.BASE / 'PG8240-prometheus-maven-coordinates-v1/manifest.json').read_text())
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in coordinates['entries'] if Path(row['path']).suffix == '.jar'}}
    stage.main()
