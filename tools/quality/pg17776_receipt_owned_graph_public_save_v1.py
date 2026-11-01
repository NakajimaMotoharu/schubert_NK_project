"""Exact original Receipt3, owned resource oracle and complete partial/natural Source proofs."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17776-receipt-owned-graph-public-save-v1'
save.BEFORE = '2ae61c645db5fc7cc854299b4ca583de924e75be'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1776', 'tools/quality/pg1777', 'tools/quality/architecture/ReceiptOwnedGraphThreeCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
