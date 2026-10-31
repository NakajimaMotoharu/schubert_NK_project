"""Exact public small-tool delta; existing held files excluded before metadata/content."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16072-jdbc-metadata-public-save-v1'
runner.BEFORE = '61cd32f587e83c5267db7ae47dc7ac7c3b1bd58f'
runner.PREFIXES += ('tools/quality/jdbc_role_metadata_v1.py', 'tools/quality/pg16068_', 'tools/quality/pg16070_', 'tools/quality/pg16072_')

if __name__ == '__main__':
    runner.main()
