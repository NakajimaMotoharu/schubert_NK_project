"""Exact public current-purpose review delta; no Product/Graph execution."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16146-readiness-purpose-public-save-v1'
runner.BEFORE = '42f50adc365c05500f4c1d3151fbbf635722871c'
runner.PREFIXES += ('tools/quality/pg16142_', 'tools/quality/pg16144_', 'tools/quality/pg16146_')

if __name__ == '__main__':
    runner.main()
