"""Exact public limited legacy-reference delta; no original runtime attestation."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16128-batch-legacy-reference-public-save-v1'
runner.BEFORE = '07204f45ace168c182cc795016de3ffe2319fc05'
runner.PREFIXES += ('tools/quality/pg16124_', 'tools/quality/pg16126_', 'tools/quality/pg16128_')

if __name__ == '__main__':
    runner.main()
