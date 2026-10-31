"""Exact public delta; held files excluded by the existing selector before metadata access."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16008-batch-run-review-public-save-v1'
runner.BEFORE = '1a065929b519ee95290b1f44880534f63bf66d49'
runner.PREFIXES += ('tools/quality/pg16004_', 'tools/quality/pg16006_', 'tools/quality/pg16008_')

if __name__ == '__main__':
    runner.main()
