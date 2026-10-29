"""Explicit public JMS owner source-context delta, not provider/graph or global acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13780-jms-owner-public-v1'
scan.BEFORE = '866ccf74e7cc6c35beeacf1c4b09bf178b189d7c'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/f03_jms_owner_six_trace.py')

if __name__ == '__main__':scan.main()
