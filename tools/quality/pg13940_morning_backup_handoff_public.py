"""Exact original whole8 backup handoff memory qualification, never real Backup/DB."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13940-morning-backup-handoff-public-v1'
scan.BEFORE = 'b84c0c0ab94851dc1f3c5cbcfc87bef5119b5bc5'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/architecture/MorningBackupHandoffCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
