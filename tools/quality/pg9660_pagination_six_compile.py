"""Fresh six compile for frozen test-only pagination candidate; no product suite is executed."""
from pathlib import Path
import json
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

if __name__ == '__main__':
    stage.SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
    stage.SLOT = stage.host.W / 'pg9660-pagination-six-compile-v1'
    stage.OUT = stage.host.BASE / 'PG9660-pagination-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE / 'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES, **{row['path']: row['sha256'] for row in entries if Path(row['path']).suffix == '.jar'}}
    stage.main()
