"""Changed public review scope scan; held names excluded before content read."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13322-null-fixture-public-v1'
scan.BEFORE = '5ef20b6696f8c3be3184a718478a12d07416e9e7'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg133')
if __name__ == '__main__':scan.main()
