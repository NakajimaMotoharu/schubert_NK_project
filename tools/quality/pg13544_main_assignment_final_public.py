"""Exact final4 Main public delta; held names excluded before any content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13544-main-assignment-final-public-v1'
scan.BEFORE = '540c0c8710603084116aa67fad3d9318d66b8dc7'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg135','tools/quality/f03_main_assignment_final_sources.py','tools/quality/f03_main_assignment_quality_v2.py')

if __name__ == '__main__':
    scan.main()
