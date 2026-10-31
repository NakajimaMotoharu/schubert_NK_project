"""Exact public reference-only delta; no Product or held path activity."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16104-resource-reference-public-save-v1'
runner.BEFORE = 'a060d1a8fb2d67b37fdee0b19a3daca052cb7c16'
runner.PREFIXES += ('tools/quality/pg16100_', 'tools/quality/pg16101_', 'tools/quality/pg16102_', 'tools/quality/pg16104_')

if __name__ == '__main__':
    runner.main()
