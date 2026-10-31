"""Exact public data-observation23 delta; exclude held files before content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16474-inspector-snapshot-public-save-v1'
save.BEFORE='a0ae4d441802b07dde2e4ee463015183181811b3'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16460_','tools/quality/pg16462_','tools/quality/pg16464_','tools/quality/pg16466_','tools/quality/pg16468_','tools/quality/pg16470_','tools/quality/pg16472_','tools/quality/pg16474_','tools/quality/architecture/InspectorSnapshotTwentyThreeCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
