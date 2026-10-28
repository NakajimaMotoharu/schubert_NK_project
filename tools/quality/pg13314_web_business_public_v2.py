"""Finite changed-public-file scan; held filenames removed before any content access."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13314-web-business-public-v2'
scan.BEFORE = '5059305e4aa9adfc551c59492238cc38074e7e1e'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg132','tools/quality/pg133')
if __name__ == '__main__':scan.main()
