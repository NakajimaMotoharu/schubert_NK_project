"""Frozen three-role GC Fake candidate guards and independent logical-close vectors; six module normal package, PT0."""
from pathlib import Path
import json
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

if __name__ == '__main__':
    stage.SOURCE = 'd1fa07bbd145ea48854b9f2b3b8be6f0f3c99dd7'
    stage.SLOT = stage.host.W/'pg11474-api-web-gc-literal-six-compile-v1'
    stage.OUT = stage.host.BASE/'PG11474-api-web-gc-literal-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix == '.jar'}}
    stage.main()




