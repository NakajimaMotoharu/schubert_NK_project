"""New corrected ternary source only; original failed PG12742 snapshot retained, PT0."""
import json
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

if __name__=='__main__':
    stage.SOURCE='f75d2fea05a98fe40d731d1a3046a64d20bbbb65'
    stage.SLOT=stage.host.W/'pg12745-metric-context-six-compile-v2'
    stage.OUT=stage.host.BASE/'PG12745-metric-context-six-compile-v2'
    stage.CAPTURE_TEST_CLASSPATH=True
    prepared=stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared)=='1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries=json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS={**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix=='.jar'}}
    stage.main()
