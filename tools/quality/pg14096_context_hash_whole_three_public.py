"""Public original-three PT and post delta only; no whole G07 assertion."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14096-context-hash-whole-three-public-v1'
scan.BEFORE = '5b1dc95c22b613bdb0a30f7074ab305502dc9597'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/architecture/ContextHashCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
