"""Exact public Main7 delta only; held names excluded before any content read."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13514-main-assignment-public-v1'
scan.BEFORE = '7b31c196c653f8bff33360a72eaf770905dbae99'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg135','tools/quality/f03_main_assignment_sources.py','tools/quality/f03_main_assignment_sources_v2.py','tools/quality/f03_main_assignment_quality.py')

if __name__ == '__main__':
    scan.main()
