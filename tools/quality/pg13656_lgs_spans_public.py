"""Exact current two-span correction delta; held names excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13656-lgs-spans-public-v1'
scan.BEFORE = '2396b80f3a7db06dbead2509ab25994e34eb1536'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/pg136', 'tools/quality/pmd_source_span_ascii.py')

if __name__ == '__main__':
    scan.main()
