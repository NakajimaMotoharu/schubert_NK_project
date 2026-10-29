"""Explicit public API primitive whole18 and periodic metadata delta, not whole PGPT acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13796-api-budget-periodic-public-v1'
scan.BEFORE = 'dd65a25d6f72a460785f448222c7929a09296aac'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/architecture/ApiStopBudgetCurrentEighteenJunitLauncher.java')

if __name__ == '__main__':scan.main()
