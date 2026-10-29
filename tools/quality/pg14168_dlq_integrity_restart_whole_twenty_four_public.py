"""Public24 supplied logical health, no actual protected-resource or restart operations."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14168-dlq-integrity-restart-whole-twenty-four-public-v1'
scan.BEFORE = 'e8910d8f463c73d5825a302288c4020e0c126290'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/SuppliedProtectedHealthCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
