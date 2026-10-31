"""Explicit public original config-test evidence and metadata only; held files excluded first."""
import pg12706_scenario_writer_public as runner

runner.OUT=runner.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16174-caddy-config-three-public-save-v1'
runner.BEFORE='c65cbc713d24d673eb4a9c4c966fd7366ef41f54'
runner.PREFIXES+=('tools/quality/pg16160_','tools/quality/pg16162_','tools/quality/pg16164_','tools/quality/pg16165_',
    'tools/quality/pg16166_','tools/quality/pg16168_','tools/quality/pg16170_','tools/quality/pg16172_','tools/quality/pg16174_',
    'tools/quality/architecture/OriginalCaddyConfigThreeJunitLauncher.java')

if __name__=='__main__':
    runner.main()
