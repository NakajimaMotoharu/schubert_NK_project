"""Exact public current-loader whole10 delta; held names excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13554-config-loaders-public-v1'
scan.BEFORE = 'cf761ac2a610e10cca6eda68ae93beaeb7d29e59'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg135','tools/quality/architecture/ConfigLoadersCurrentJunitLauncher.java')

if __name__ == '__main__':
    scan.main()
