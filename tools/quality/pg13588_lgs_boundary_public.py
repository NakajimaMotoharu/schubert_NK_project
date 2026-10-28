"""Exact current LGS public text delta; held paths excluded before any content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13588-lgs-boundary-public-v1'
scan.BEFORE = '3927eab38aa76da66bcc0c4bb7fe4a3b2677c49f'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/pg135', 'tools/quality/f03_lgs_boundary_',
    'tools/quality/architecture/LgsBoundaryCurrentJunitLauncher.java',
    'tools/quality/architecture/ComponentCoverageDiagnostic.java')

if __name__ == '__main__':
    scan.main()
