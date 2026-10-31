"""Exact administrative reference-defect closure only; no target activity."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16080-review-reference-closure-public-save-v1'
runner.BEFORE = '7dc9c306ca4abbbff94babf80c1cb2fa28402607'
runner.PREFIXES += ('tools/quality/pg16080_',)

if __name__ == '__main__':
    runner.main()
