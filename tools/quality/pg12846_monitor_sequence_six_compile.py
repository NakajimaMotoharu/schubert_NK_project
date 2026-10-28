"""One fixed Test-only source; six normal compile/format/null/lint, product PT0."""
import json
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

if __name__=='__main__':
    stage.SOURCE='f8ad1ae16aa52db0119fefbad9e2cea6d6affe55'
    stage.SLOT=stage.host.W/'pg12846-monitor-sequence-six-compile-v1'
    stage.OUT=stage.host.BASE/'PG12846-monitor-sequence-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    prepared=stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared)=='1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries=json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS={**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix=='.jar'}}
    stage.main()
