"""Exact Unit5 public delta, preserved failed tools; exclude held paths before metadata/content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16616-application-unit-public-save-v1'
save.BEFORE='fd5d6f502d16e0b3a99e72616c2f84cd471dad3c'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16604_','tools/quality/pg16605_','tools/quality/pg16606_','tools/quality/pg16607_','tools/quality/pg16608_','tools/quality/pg16610_','tools/quality/pg16612_','tools/quality/pg16614_','tools/quality/pg16616_','tools/quality/architecture/ApplicationUnitFiveCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
