"""Public static Source contract refs; no waiver, Product PT, runtime or whole quality claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14196-main-failure-boundaries-sixty-two-public-v1'
scan.BEFORE = '380d223f2447cd699a21803f990399bf0a3803a2'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/f03_main_failure_boundary_sixty_two_trace_v1.py')

if __name__ == '__main__':scan.main()
