"""Public original13/two complete Source technical evidence delta only."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14120-batch-metric-whole-thirteen-public-v1'
scan.BEFORE = '591081565f7bf548c0d8f694a5a6c26ec28f3cb3'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/BatchMetricCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
