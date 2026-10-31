"""Explicit public changed text only, no held-file metadata or content access."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16246-public-proof-eight-public-save-v1'
save.BEFORE='88c715aefe1891063341b9121973754ea38eb2c2'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16232_','tools/quality/pg16234_',
    'tools/quality/pg16236_','tools/quality/pg16238_','tools/quality/pg16240_','tools/quality/pg16241_',
    'tools/quality/pg16242_','tools/quality/pg16244_','tools/quality/pg16246_',
    'tools/quality/architecture/PublicProofEightJunitLauncher.java')

if __name__=='__main__':save.main()
