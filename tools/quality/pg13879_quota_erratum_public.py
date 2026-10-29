"""Public three-document append-only quota correction, no source or Product test change."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13879-quota-erratum-public-v1'
scan.BEFORE = 'a1bd76c5208b51d9b0a750bf64799bedbdc5d377'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138')

if __name__ == '__main__':scan.main()
