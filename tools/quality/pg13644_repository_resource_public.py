"""Exact public repository-context/tool-correction delta; held names excluded before access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13644-repository-resource-public-v1'
scan.BEFORE = '396e7008418cb265cf8b10d5089719357957bcab'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/pg136', 'tools/quality/f03_repository_resource_trace.py')

if __name__ == '__main__':
    scan.main()
