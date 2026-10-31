"""Public saved static identity references, no type checker or Product operation."""
import pg12706_scenario_writer_public as runner

runner.OUT=runner.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16208-throwable-identity-reference-public-save-v1'
runner.BEFORE='064a43926a6f7f2760395a48435e34a00a238bc4'
runner.PREFIXES+=('tools/quality/pg16204_','tools/quality/pg16206_','tools/quality/pg16208_')

if __name__=='__main__':
    runner.main()
