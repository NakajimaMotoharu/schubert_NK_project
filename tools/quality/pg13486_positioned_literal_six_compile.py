"""One fixed-source normal six-module build; compile Tests without executing any."""
import json
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
import pg13481_positioned_literal_config_v2 as cfg
from f03_literal_batch_sources import out

if __name__ == '__main__':
    stage.SOURCE = 'ff8149dd27decbe683b48d1cbb5f2cb59ecca83a'
    stage.OUT = out(cfg,cfg.NORMAL_NUMBER)
    stage.SLOT = stage.host.W/stage.OUT.name.lower()
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix == '.jar'}}
    stage.main()
