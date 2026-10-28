"""Bound public nine-field visibility review delta; no product actions or global scan claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13722-main-volatile-public-v1'
scan.BEFORE = '2523453f3e0cf3716d437f3cd26a2444fba4d081'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/f03_main_volatile_trace.py')

if __name__ == '__main__':scan.main()
