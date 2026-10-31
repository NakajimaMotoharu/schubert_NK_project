"""Public exact review/failure delta only, held paths excluded before metadata access."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16064-cleanup-terminal-review-public-save-v1'
runner.BEFORE = 'c56fefd7482d6a3db5855645ae184e121cb9f008'
runner.PREFIXES += ('tools/quality/pg16058_', 'tools/quality/pg16060_', 'tools/quality/pg16061_', 'tools/quality/pg16062_', 'tools/quality/pg16064_')

if __name__ == '__main__':
    runner.main()
