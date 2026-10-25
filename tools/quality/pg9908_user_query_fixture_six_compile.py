"""Explicit-import/local-literal Test candidate, normal compile only; no fixtures or Tests run."""
from pathlib import Path
import json
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

if __name__ == '__main__':
    stage.SOURCE = '4c94a7d4665e4f3c27a7d39fb2b427bec663d903'
    stage.SLOT = stage.host.W/'pg9908-user-query-fixture-six-compile-v1'
    stage.OUT = stage.host.BASE/'PG9908-user-query-fixture-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix == '.jar'}}
    stage.main()
