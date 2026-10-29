"""Public release-claims value whole8 and complete-unit counters; no authority artifacts."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13876-release-approval-public-v1'
scan.BEFORE = '3dbc5966e53bd2b6c15ec09b5b4a250e150546ad'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138','tools/quality/architecture/ReleaseApprovalValueCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
