"""Public current snapshot literal correction and original qualification evidence only."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13830-snapshot-literal-fix-public-v1'
scan.BEFORE = '23582a606b50efbea63442b7a8487d1c9f2e7035'
scan.PREFIXES = (*scan.PREFIXES,'src/','tools/quality/pg138','tools/quality/snapshot_program_qualification.py','tools/quality/architecture/InspectorSnapshotWholeProgramJunitLauncher.java')

if __name__ == '__main__':scan.main()
