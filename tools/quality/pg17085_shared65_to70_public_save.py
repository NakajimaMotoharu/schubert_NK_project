"""Exact public mandatory shared65-to70 review; no Product reexecution."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17085-shared65-to70-public-save-v1'
save.BEFORE='04e02a0df7ce06b73cf0006b05fd1f357caca276'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg17085_')
if __name__=='__main__':save.main()
