"""One fixed-source six-module normal build after149 literal-only corrections; Product PT0."""
import json
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
import pg13301_web_business_literal_config_v2 as cfg
from f03_literal_batch_sources import out
if __name__ == '__main__':
    stage.SOURCE = '81a1b0c32be8167c07320e6bfaf469bcd44eb7bd'
    stage.OUT = out(cfg,cfg.NORMAL_NUMBER);stage.SLOT = stage.host.W/stage.OUT.name.lower();stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix == '.jar'}}
    stage.main()
