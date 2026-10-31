"""Exact public empty-catch references; no dynamic product actions."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16158-emptycatch-reference-public-save-v1'
runner.BEFORE = '871a21015897ad0a436f682cfcc6f8355b2281f8'
runner.PREFIXES += ('tools/quality/pg16154_', 'tools/quality/pg16156_', 'tools/quality/pg16158_')

if __name__ == '__main__':
    runner.main()
