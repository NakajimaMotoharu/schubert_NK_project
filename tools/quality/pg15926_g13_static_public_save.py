"""Exact public delta for the static descriptor group, held paths excluded first."""
import pg12706_scenario_writer_public as runner

runner.OUT = runner.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15926-g13-static-public-save-v1'
runner.BEFORE = 'c67107a129aded9e945ca6130a3acc35c1dfd20c'
runner.PREFIXES += ('tools/quality/pg159',)

if __name__ == '__main__':
    runner.main()
