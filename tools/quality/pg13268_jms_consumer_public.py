"""Changed public review artifacts only; held files excluded before content access."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13268-jms-consumer-public-v1'
scan.BEFORE = 'c795452aa07451133a89d7b4717fe61e1cf3d641'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg132')
if __name__ == '__main__':scan.main()
