"""Exact administrative closure delta only; no regression or target activity."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16066-review-defect-closure-public-save-v1'
runner.BEFORE = 'fc2189382d4626464f895af48e8b8a7db734baea'
runner.PREFIXES += ('tools/quality/pg16066_',)

if __name__ == '__main__':
    runner.main()
