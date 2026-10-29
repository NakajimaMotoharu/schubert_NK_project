"""Public metadata side overlay only, not Product execution or whole quality acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14180-current-host-program-measurements-24exec-public-v2'
scan.BEFORE = '4541a217dd17e64d4daff9390b63b41ea791afd9'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141')

if __name__ == '__main__':scan.main()
