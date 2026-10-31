"""Exact public modern reference correction delta; no target operations."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16140-systemd-apiro-reference-public-save-v1'
runner.BEFORE = '04b8c122d8ad4245e3df0cb098807433d41d3e14'
runner.PREFIXES += ('tools/quality/pg16136_', 'tools/quality/pg16137_', 'tools/quality/pg16138_', 'tools/quality/pg16140_')

if __name__ == '__main__':
    runner.main()
