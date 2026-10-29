"""Public21 pure value-contract and complete Source technical evidence only."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14132-metric-mode-retention-whole-twenty-one-public-v1'
scan.BEFORE = '29f2c2b554fb05a3a70dafc5690215afaf094058'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/MetricModeCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
