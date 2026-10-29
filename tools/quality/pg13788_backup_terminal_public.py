"""Explicit public terminal projection whole3 evidence, not whole DB/Backup acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13788-backup-terminal-public-v1'
scan.BEFORE = '2853e66f91348cd49340e12657a20b6caa388e44'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/architecture/BackupTerminalCurrentThreeJunitLauncher.java')

if __name__ == '__main__':scan.main()
