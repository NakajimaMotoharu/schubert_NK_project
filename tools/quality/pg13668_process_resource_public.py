"""Exact public current ProcessResource whole7 evidence and periodic report delta; held files excluded."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13668-process-resource-public-v1'
scan.BEFORE = '7721271601e4b714d17245e4ee8a69e0920672f8'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/pg136', 'tools/quality/architecture/ProcessResourceCurrentJunitLauncher.java')

if __name__ == '__main__':
    scan.main()
