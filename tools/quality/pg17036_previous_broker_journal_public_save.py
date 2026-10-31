"""Exact public PreviousBroker memory journal four delta; no actual journal/service action."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17036-previous-broker-journal-public-save-v1'
save.BEFORE='c63e9e6ce9a96eb51f565fdd6f8c7a40c06d79b0'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg17022_','tools/quality/pg17024_','tools/quality/pg17026_','tools/quality/pg17028_','tools/quality/pg17030_','tools/quality/pg17032_','tools/quality/pg17034_','tools/quality/pg17036_','tools/quality/architecture/PreviousBrokerMemoryJournalFourCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
