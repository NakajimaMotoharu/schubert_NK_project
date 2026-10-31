"""Exact public Root-proof callback/data qualification; exclude held files before access."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16806-public-root-proof-public-save-v1'
save.BEFORE='180fedb09ec91cdafb237c98c64369ec744a999c'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16792_','tools/quality/pg16793_','tools/quality/pg16794_','tools/quality/pg16796_','tools/quality/pg16798_','tools/quality/pg16800_','tools/quality/pg16802_','tools/quality/pg16804_','tools/quality/pg16806_','tools/quality/architecture/PublicRootProofFourCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
