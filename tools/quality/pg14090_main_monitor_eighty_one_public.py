"""Public pending Source-reference delta; three format patterns, not whole G07."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14090-main-monitor-eighty-one-public-v1'
scan.BEFORE = '189a0a632e623f4da61138787d78979b7a4fb246'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/static_context_reader_v2.py','tools/quality/static_context_post_v3.py','tools/quality/f03_main_monitor_eighty_one_trace.py','tools/quality/f03_main_monitor_eighty_one_trace_v2.py')

if __name__ == '__main__':scan.main()
