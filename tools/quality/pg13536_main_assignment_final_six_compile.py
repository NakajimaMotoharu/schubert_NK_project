"""Fixed-source six standard modules; compile-only, no Product Tests or application lifecycle."""
import json
from pathlib import Path
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
import pg13530_main_assignment_final_config as cfg
from f03_literal_batch_sources import out

if __name__ == '__main__':
    stage.SOURCE = 'a90e303fc59938d413c2d777380bdffbe3e7f9e7'
    stage.OUT = out(cfg,cfg.NORMAL_NUMBER)
    stage.SLOT = stage.host.W/stage.OUT.name.lower()
    stage.CAPTURE_TEST_CLASSPATH = True
    prepared = stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared) == '1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    entries = json.loads(prepared.read_bytes())['entries']
    stage.DEPENDENCY_JARS = {**sdk.DEPENDENCIES,**{row['path']:row['sha256'] for row in entries if Path(row['path']).suffix == '.jar'}}
    stage.main()
