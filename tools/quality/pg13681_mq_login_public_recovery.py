"""Bound public delta check using the existing ROOT contract; no product actions."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13681-mq-login-public-recovery-v1'
scan.BEFORE = '19ecd47a98bd4dcdbe10bb087541e7bf4ff55d1a'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg136','tools/quality/architecture/MqLoginCurrentJunitLauncher.java','tools/quality/architecture/MqLoginCurrentSixJunitLauncher.java')

if __name__ == '__main__':scan.main()
