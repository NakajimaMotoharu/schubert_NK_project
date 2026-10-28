"""Bound public twelve-case journal result delta; no product actions or global scan claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13696-broker-journal-public-v1'
scan.BEFORE = '671a0fd194f85cce1091af1a0e094efb29c11804'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg136','tools/quality/architecture/BrokerJournalCurrentTwelveJunitLauncher.java')

if __name__ == '__main__':scan.main()
