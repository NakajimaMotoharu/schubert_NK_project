"""Exact public saved-session-reference delta; no Product or target operations."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16116-batch-session-reference-public-save-v1'
runner.BEFORE = 'eefb17abc6b00d988c0b4ac3e95306af5b182dc9'
runner.PREFIXES += ('tools/quality/pg16112_', 'tools/quality/pg16114_', 'tools/quality/pg16116_')

if __name__ == '__main__':
    runner.main()
