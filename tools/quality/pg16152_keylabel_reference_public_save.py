"""Exact public reference delta, without product or external execution."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16152-keylabel-reference-public-save-v1'
runner.BEFORE = '91393aae3c9358dfc165d1ee4cca5a566d9c971f'
runner.PREFIXES += ('tools/quality/pg16148_', 'tools/quality/pg16150_', 'tools/quality/pg16152_')

if __name__ == '__main__':
    runner.main()
