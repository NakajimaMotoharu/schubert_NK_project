"""Save four public stored metadata qualifications; no private keys or held tool access."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18186-inbox-stored-metadata-public-save-v1'
save.BEFORE='4d486929dd463b149973c4abb627f5d77170d157'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1817','tools/quality/pg1818','tools/quality/architecture/StoredMetadataContractTest.java','tools/quality/architecture/StoredMetadataSixCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
