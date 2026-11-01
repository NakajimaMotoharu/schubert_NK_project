"""Save pure immutable Web log claim value proofs."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18396-weblog-claim-public-save-v1'
save.BEFORE='ce284deb86508071d03cf913ce94344f2e49bc9a'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1838','tools/quality/pg1839','tools/quality/architecture/WebLogClaimValueContractTest.java','tools/quality/architecture/WebLogClaimSixCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
