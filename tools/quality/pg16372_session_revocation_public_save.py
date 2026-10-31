"""Exact public session/revocation purpose delta; no Product or session operation."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16372-session-revocation-public-save-v1'
save.BEFORE='21e218b3418c45ca5835cbff8ac0ba9a6d282472'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16368_',
    'tools/quality/pg16370_','tools/quality/pg16372_')

if __name__=='__main__':save.main()
