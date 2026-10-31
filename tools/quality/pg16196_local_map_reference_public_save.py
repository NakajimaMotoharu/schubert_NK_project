"""Exact public saved-map-reference delta, never execute map/retirement/Backup code."""
import pg12706_scenario_writer_public as runner

runner.OUT=runner.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16196-local-map-reference-public-save-v1'
runner.BEFORE='3ed3e1c3bbf0543dcf92ad11c6c4c75078fd3122'
runner.PREFIXES+=('tools/quality/pg16192_','tools/quality/pg16194_','tools/quality/pg16196_')

if __name__=='__main__':
    runner.main()
