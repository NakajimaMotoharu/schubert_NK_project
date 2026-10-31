"""Exact public reference/schema correction delta; held paths excluded before metadata/content."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16078-four-repository-reference-public-save-v1'
runner.BEFORE = 'd37781bcbfd8a70c9bd67ff44f351b9c88ba458a'
runner.PREFIXES += ('tools/quality/pg16074_', 'tools/quality/pg16075_', 'tools/quality/pg16076_', 'tools/quality/pg16078_')

if __name__ == '__main__':
    runner.main()
