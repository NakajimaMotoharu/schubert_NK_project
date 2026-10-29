"""Nine public source refs, all raw warnings and actual-operation HOLDs retained."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13984-last-main-resource-nine-public-v1'
scan.BEFORE = '28f97b1577fd937aa92277413bab17dd1385b40a'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/f03_last_main_resource_nine_trace.py')

if __name__ == '__main__':scan.main()
