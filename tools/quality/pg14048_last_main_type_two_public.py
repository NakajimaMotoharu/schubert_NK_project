"""Last bounded type-reference public delta; all raw/runtime quality holds retained."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14048-last-main-type-two-public-v1'
scan.BEFORE = '7b9d73bbbba774eef832db0f6ad4ec82724d3eaa'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/f03_last_main_type_two_trace.py')

if __name__ == '__main__':scan.main()
