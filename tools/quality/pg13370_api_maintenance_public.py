"""Exact public text delta only, held names subtracted before access; no target execution."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13370-api-maintenance-public-v1'
scan.BEFORE = 'f35a1ae26b49a66217127a4f532324dbded26257'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg133','tools/quality/f03_literal_batch_quality_v2.py','tools/quality/f03_literal_batch_trace_v2.py','tools/quality/f03_literal_batch_preflight_v3.py')
if __name__ == '__main__':scan.main()
