"""Batch type-priority review, failed tool and explicit correction retained."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14024-batch-transaction-type-priority-public-v1'
scan.BEFORE = '2c7516fa04fc73f934628923db59ed95acf88bc1'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140')

if __name__ == '__main__':scan.main()
