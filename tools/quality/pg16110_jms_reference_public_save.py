"""Exact public saved-JMS-reference metadata delta, no target operations."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16110-jms-reference-public-save-v1'
runner.BEFORE = 'ffdadf636772f26eb33802576f6fe5092e3cd5ce'
runner.PREFIXES += ('tools/quality/pg16106_', 'tools/quality/pg16108_', 'tools/quality/pg16110_')

if __name__ == '__main__':
    runner.main()
