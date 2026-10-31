"""Public current-purpose and finite tooling-failure evidence only, no release execution."""
import pg12706_scenario_writer_public as runner

runner.OUT=runner.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16202-release-map-purpose-public-save-v1'
runner.BEFORE='2048d20f21cb9b0f4520206e146f3fb0b12c50b3'
runner.PREFIXES+=('tools/quality/pg16198_','tools/quality/pg16199_','tools/quality/pg16200_','tools/quality/pg16202_')

if __name__=='__main__':
    runner.main()
