"""Save only explicit public F03 source-bound observation metadata and tool failures."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15936-f03-main-public-save-v1'
runner.BEFORE = '65c1113c32feb12bc7509c37d1fdf2ba3e76e9a3'
runner.PREFIXES += ('tools/quality/pg159',)

if __name__ == '__main__':
    runner.main()
