"""Public16 supplied transfer metric/health evidence, not actual transfer-resource qualification."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14174-transfer-metric-health-whole-sixteen-public-v1'
scan.BEFORE = '6ee61a6a805b9fa5b690caf68e5d8e8385895d1f'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/TransferMetricCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
