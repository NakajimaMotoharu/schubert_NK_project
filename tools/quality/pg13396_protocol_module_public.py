"""Exact public delta; held files excluded before access; no Product execution."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13396-protocol-module-public-v1'
scan.BEFORE = '18538fce8b5471ae33140859747e788ca6d48e43'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg133')

if __name__ == '__main__':
    scan.main()
