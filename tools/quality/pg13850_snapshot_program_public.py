"""Explicit public whole-program qualification and retained unsuccessful draft evidence."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13850-snapshot-program-public-v1'
scan.BEFORE = '0061d178cda80c2ce3926290619c64db125dbcfc'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138','tools/quality/snapshot_program_qualified_v2.py','tools/quality/f03_snapshot_program_trace.py','tools/quality/architecture/InspectorSnapshotQualifiedProgramJunitLauncher.java')

if __name__ == '__main__':scan.main()
