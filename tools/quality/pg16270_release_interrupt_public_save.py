"""Exact explicit public delta scan and save, no held-content or whole-G07 assertion."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16270-release-interrupt-public-save-v1'
save.BEFORE='d097a7dc2d695aa7dfbb36a6df61a3584e2234a7'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16266_',
    'tools/quality/pg16268_','tools/quality/pg16269_','tools/quality/pg16270_')

if __name__=='__main__':save.main()
