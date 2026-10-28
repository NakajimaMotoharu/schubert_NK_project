"""Exact public text delta only; held names removed before reading content."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13424-outbox-value-public-v1'
scan.BEFORE = 'fc34fc3db9ff0583464df7ba71d687e0568ba1a6'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg134','tools/quality/architecture/OutboxCurrentValueJunitLauncher.java')

if __name__ == '__main__':
    scan.main()
