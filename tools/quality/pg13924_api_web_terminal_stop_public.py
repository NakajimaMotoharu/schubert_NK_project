"""Exact original whole11 and independent partial counters, plus preserved tool failure."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13924-api-web-terminal-stop-public-v1'
scan.BEFORE = '0623063f50183584f35e7cf0e692441116966062'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/architecture/ApiWebTerminalStopMemoryJunitLauncher.java')

if __name__ == '__main__':scan.main()
