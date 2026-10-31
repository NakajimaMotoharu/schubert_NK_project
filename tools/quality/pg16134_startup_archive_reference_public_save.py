"""Exact public two-legacy reference correction delta; held and actual operations excluded."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16134-startup-archive-reference-public-save-v1'
runner.BEFORE = '5598c511cc11ce4f518dd32dd85f8d00a3d48d4f'
runner.PREFIXES += ('tools/quality/pg16130_', 'tools/quality/pg16131_', 'tools/quality/pg16132_', 'tools/quality/pg16134_')

if __name__ == '__main__':
    runner.main()
