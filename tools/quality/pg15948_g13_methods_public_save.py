"""Exact public delta for current passive Main method denominator."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15948-g13-methods-public-save-v1'
runner.BEFORE = 'f06560c6373e4f2876b1466e69ec7397a20dcd72'
runner.PREFIXES += ('tools/quality/pg159',)

if __name__ == '__main__':
    runner.main()
