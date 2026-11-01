"""Save same-source principal boundary proofs without held files or product replay."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17926-session-principal-public-save-v1'
save.BEFORE='bec06882d4cdba94a6dbf556a8b4f6ae9913bf3e'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg179','tools/quality/architecture/SessionPrincipalBoundaryContractTest.java','tools/quality/architecture/SessionPrincipalBoundaryFiveCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
