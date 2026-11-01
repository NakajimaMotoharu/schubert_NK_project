"""Save limited public operator-source evidence, without claiming G07 closure."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18404-g07-operator-source-public-save-v1'
save.BEFORE='cc388c2f491ff2600fc0757ee9c369b90e774dd6'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1840')
if __name__=='__main__':save.main()
