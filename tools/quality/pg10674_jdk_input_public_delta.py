"""Explicit fixed-JDK-input public delta; held names excluded before content access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'e1dcc2670'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10674-jdk-input-public-delta-v1'
    stage.main()
