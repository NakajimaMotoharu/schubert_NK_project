"""Public raw-reference/tool-correction delta only, actual operations stay held."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14008-jms-type-priority-seventeen-public-v1'
scan.BEFORE = '3ba2eca6135108c7b44d48fe5217a2856d2c1f00'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/f03_jms_type_priority_seventeen_trace')

if __name__ == '__main__':scan.main()
