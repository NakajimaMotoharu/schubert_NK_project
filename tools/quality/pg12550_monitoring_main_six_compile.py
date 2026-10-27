"""Frozen pure monitoring Main two-source correction; six normal packages/PT0, no product run."""
import json
import sys
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

if __name__=='__main__':
    assert len(sys.argv)==2 and len(sys.argv[1])==40 and all(c in '0123456789abcdef' for c in sys.argv[1])
    stage.SOURCE=sys.argv[1]
    stage.SLOT=stage.host.W/'pg12550-monitoring-main-six-compile-v1'
    stage.OUT=stage.host.BASE/'PG12550-monitoring-main-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    prepared=stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared)=='1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries=json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS={**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix=='.jar'}}
    stage.main()
