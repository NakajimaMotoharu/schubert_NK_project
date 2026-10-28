"""Exact public whole16 evidence delta; held names excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13524-primitive-owner-public-v1'
scan.BEFORE = '49f2f003c3859aa730506884145d06d08cc6b198'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg135','tools/quality/architecture/PrimitiveOwnerCurrentJunitLauncher.java')

if __name__ == '__main__':
    scan.main()
