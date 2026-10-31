"""Exact public final-v4 static reference delta only."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16122-main-nonempty-reference-public-save-v1'
runner.BEFORE = 'cc3ce21475af7b848ce8a207122ecdd1bfd3dd12'
runner.PREFIXES += ('tools/quality/pg16118_', 'tools/quality/pg16120_', 'tools/quality/pg16122_')

if __name__ == '__main__':
    runner.main()
