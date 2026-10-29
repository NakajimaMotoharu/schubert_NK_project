"""Public33 supplied backlog/Backup state proof, never actual broker or Backup execution."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14162-supplied-backlog-backup-whole-thirty-three-public-v1'
scan.BEFORE = '68f2142c4bda94c34f9b90eb0cdafbc982316629'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/SuppliedBacklogCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
