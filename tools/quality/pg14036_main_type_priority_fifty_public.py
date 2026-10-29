"""Public source-reason batch join; original warnings, holds and formal state retained."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14036-main-type-priority-fifty-public-v1'
scan.BEFORE = 'd08abbd3edf8c29424ffffdfaaeb3bff3e1aeb21'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/f03_main_type_priority_fifty_trace.py')

if __name__ == '__main__':scan.main()
