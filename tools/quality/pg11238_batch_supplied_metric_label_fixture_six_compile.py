"""Frozen Batch supplied metric/label Test fixture changes; six module normal package, PT0."""
from pathlib import Path
import json
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

if __name__ == '__main__':
    stage.SOURCE = 'ef86a244b2f528a2d60bd0f22a94a853ce3146ff'
    stage.SLOT = stage.host.W/'pg11238-batch-supplied-metric-label-fixture-six-compile-v1'
    stage.OUT = stage.host.BASE/'PG11238-batch-supplied-metric-label-fixture-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix == '.jar'}}
    stage.main()




