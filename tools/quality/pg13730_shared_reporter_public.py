"""Bound public shared-reporter tool-only evidence delta; no product or global scan claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13730-shared-reporter-public-v1'
scan.BEFORE = '26f3c2a8cb958c6a370f7fca831140a9f38b02ed'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/architecture/SharedSelectedJunitReporterV1.java','tools/quality/architecture/ReporterToolFixturesV1.java','tools/quality/architecture/ReporterToolDriverV1.java')

if __name__ == '__main__':scan.main()
