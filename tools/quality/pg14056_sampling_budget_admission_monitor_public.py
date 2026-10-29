"""Public private-monitor review only; no warning removal or dynamic acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14056-sampling-budget-admission-monitor-public-v1'
scan.BEFORE = 'c0fa99aa86630813af46fbb08365dde142838deb'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140')

if __name__ == '__main__':scan.main()
