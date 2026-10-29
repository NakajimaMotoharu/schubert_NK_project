"""Public whole2 memory lifecycle result, retaining complete-unit coverage gaps."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13886-web-runtime-public-v1'
scan.BEFORE = '7a388d434445ad7744611b0b2e3539fd8e9aa7c2'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138','tools/quality/architecture/WebRuntimeExecutionCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
