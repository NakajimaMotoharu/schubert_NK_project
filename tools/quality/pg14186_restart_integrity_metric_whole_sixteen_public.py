"""Public16 supplied counters only, not actual process or integrity operations."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14186-restart-integrity-metric-whole-sixteen-public-v1'
scan.BEFORE = '9040b21ecf9814b894655b51fad80aea69b8e31c'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/RestartIntegrityMetricCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
