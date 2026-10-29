"""Original whole-six public evidence delta, no external owner/native claims."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14016-maintenance-parent-guard-whole-six-public-v1'
scan.BEFORE = 'd16bd77f5b109cd73367fb254518d21f927a76b3'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/architecture/MaintenanceParentGuardCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
