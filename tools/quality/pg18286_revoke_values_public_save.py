"""Save revocation projection proofs, preserving held inputs and old clock correction."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18286-revoke-values-public-save-v1'
save.BEFORE='d541892cb719d15119abf2a19a837c8b84cb181d'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1827','tools/quality/pg1828','tools/quality/architecture/RevokeProjectionValueContractTest.java','tools/quality/architecture/RevokeValuesTenCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
