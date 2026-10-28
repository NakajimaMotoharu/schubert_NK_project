"""Exact public document/path correction; held names excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13496-positioned-record-public-v1'
scan.BEFORE = '1b30bc3ef5de3dfafef10eb7f26b13639cc993e8'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg134')

if __name__ == '__main__':
    scan.main()
