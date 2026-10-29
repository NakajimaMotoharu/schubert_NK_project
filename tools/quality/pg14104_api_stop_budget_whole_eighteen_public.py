"""Public original18/source qualification and canonical correction delta only."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14104-api-stop-budget-whole-eighteen-public-v1'
scan.BEFORE = 'b29223a3ec5297a5f2ce64f10b6e62a2996f9a5f'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/pg141','tools/quality/architecture/ApiStopBudgetCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
