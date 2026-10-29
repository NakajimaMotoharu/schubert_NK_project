"""Public management static refs, no product or actual owner operations."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13996-management-catch-priority-eight-public-v1'
scan.BEFORE = '928444e8a43b1d3668fe48a399e1fcfbeefc0457'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/f03_management_catch_priority_eight_trace.py')

if __name__ == '__main__':scan.main()
