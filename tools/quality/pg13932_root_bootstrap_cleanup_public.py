"""Exact whole16 memory boundaries and explicit native/admin coverage gaps."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13932-root-bootstrap-cleanup-public-v1'
scan.BEFORE = '1d8278578593a63db3dae8ac494e7d42c6529b1a'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/architecture/RootBootstrapCleanupMemoryJunitLauncher.java')

if __name__ == '__main__':scan.main()
