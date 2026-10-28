"""One immutable snapshot normal build for six mechanical Test changes; all Product PT remains unrun."""
import json
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
import pg13223_db_web_literal_config as cfg
from f03_literal_batch_sources import out

if __name__ == '__main__':
    stage.SOURCE = '1762d68747c3460afd90a03377858572dfc25931'
    stage.OUT = out(cfg,cfg.NORMAL_NUMBER)
    stage.SLOT = stage.host.W/stage.OUT.name.lower()
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{r['path']:r['sha256'] for r in entries if Path(r['path']).suffix == '.jar'}}
    stage.main()
