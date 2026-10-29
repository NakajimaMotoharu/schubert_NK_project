"""New API context and scoped tool correction public delta only."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14070-api-dispatch-observation-monitor-public-v1'
scan.BEFORE = '96324b53c9dcc2eb67ae49bf426a047fec7b9ec9'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140')

if __name__ == '__main__':scan.main()
