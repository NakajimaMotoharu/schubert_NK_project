"""Exact public delta only; held names are removed before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13476-residual-literal-public-v1'
scan.BEFORE = '800e638bfac9d7eff5c7c0d63f6662e36e563fa0'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg134')

if __name__ == '__main__':
    scan.main()
