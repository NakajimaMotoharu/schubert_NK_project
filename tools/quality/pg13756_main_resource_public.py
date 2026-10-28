"""Explicit public six-resource-context delta, not global scan/coverage acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13756-main-resource-public-v1'
scan.BEFORE = '531c077b4d21917698d2613aefcf3d19af9f9dad'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/f03_main_resource_six_trace.py')

if __name__ == '__main__':scan.main()
