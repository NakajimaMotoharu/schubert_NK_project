"""Public delta, held paths excluded before metadata/content."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15942-f03-schema-public-save-v1'
runner.BEFORE = '6d97a17ea3a8c059ae648ff9297755719c249445'
runner.PREFIXES += ('tools/quality/pg159',)

if __name__ == '__main__':
    runner.main()
