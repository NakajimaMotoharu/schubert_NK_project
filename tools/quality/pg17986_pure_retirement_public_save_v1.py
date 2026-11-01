"""Save pure retirement record evidence, no actual retirement or held source access."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17986-pure-retirement-public-save-v1'
save.BEFORE='a050e523d59b6664930fd5a6a0b653978ee41acb'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1797','tools/quality/pg1798','tools/quality/architecture/PureRetirementCodecContractTest.java','tools/quality/architecture/PureRetirementTwelveCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
