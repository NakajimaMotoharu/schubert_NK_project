"""Current read-only LGS context evidence delta; held paths excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13624-lgs-context-public-v1'
scan.BEFORE = 'bc73445aeb973020ed9d4fd6581a0b1082e12179'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/pg136')

if __name__ == '__main__':
    scan.main()
