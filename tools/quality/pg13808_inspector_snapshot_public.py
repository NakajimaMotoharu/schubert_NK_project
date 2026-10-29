"""Explicit public fixed-text snapshot whole9 delta, not Unit/Root/native acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13808-inspector-snapshot-public-v1'
scan.BEFORE = '929e6de6752cc1764a4783104bed1339b1186efa'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138','tools/quality/architecture/InspectorSnapshotCurrentNineJunitLauncher.java')

if __name__ == '__main__':scan.main()
