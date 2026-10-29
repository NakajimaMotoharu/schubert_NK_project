"""Public bounded periodic evidence comparison, no whole secret scan assertion."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14108-used41-periodic-public-v1'
scan.BEFORE = 'd8964caf914d0149b4174d068ccb548b3bcf9e5a'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141')

if __name__ == '__main__':scan.main()
