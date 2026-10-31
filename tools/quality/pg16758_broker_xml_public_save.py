"""Exact broker public-XML delta, excluding held names before metadata/content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16758-broker-xml-public-save-v1'
save.BEFORE='f2cdc73be22ff4dc345262589a9a240e370c5f95'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16744_','tools/quality/pg16746_','tools/quality/pg16748_','tools/quality/pg16750_','tools/quality/pg16752_','tools/quality/pg16753_','tools/quality/pg16754_','tools/quality/pg16756_','tools/quality/pg16758_','tools/quality/architecture/BrokerXmlFourCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
