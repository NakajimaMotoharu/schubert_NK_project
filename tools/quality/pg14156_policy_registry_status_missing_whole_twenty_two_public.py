"""Public22 pure policy/status qualification; no actual protected-resource operations."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14156-policy-registry-status-missing-whole-twenty-two-public-v1'
scan.BEFORE = 'b75e279b2a8e65b987c34851a8f9e2763f04f66c'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/PolicyRegistryCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
