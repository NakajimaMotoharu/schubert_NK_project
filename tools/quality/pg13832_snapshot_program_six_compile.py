"""Fresh fixed-source six-module compile/null/format, PT deliberately unrun."""
import json
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
OUT = stage.host.BASE/'PG13832-snapshot-program-six-compile-v1'
SLOT = stage.host.W/'pg13832-snapshot-program-six-compile-v1'

if __name__ == '__main__':
    stage.SOURCE = SOURCE
    stage.OUT = OUT
    stage.SLOT = SLOT
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{row['path']:row['sha256'] for row in entries if Path(row['path']).suffix == '.jar'}}
    stage.main()
