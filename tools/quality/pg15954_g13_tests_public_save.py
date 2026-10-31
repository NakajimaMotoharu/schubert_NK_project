"""Exact public delta for Test declaration denominator, no held file access."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15954-g13-tests-public-save-v1'
runner.BEFORE = '59b042869d824a3f41111741162709eda29413c8'
runner.PREFIXES += ('tools/quality/pg159',)

if __name__ == '__main__':
    runner.main()
