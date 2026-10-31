"""Exact public monitor/visibility reference delta, no Product or native side effects."""
import pg12706_scenario_writer_public as runner

runner.OUT=runner.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16214-concurrency-reference-public-save-v1'
runner.BEFORE='2dd6d0fbc31cccdbfd547c5954f6ccccbc0ae1a4'
runner.PREFIXES+=('tools/quality/pg16210_','tools/quality/pg16212_','tools/quality/pg16214_')

if __name__=='__main__':
    runner.main()
