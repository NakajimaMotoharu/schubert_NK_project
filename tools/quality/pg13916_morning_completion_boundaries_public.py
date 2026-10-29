"""Exact whole13 public evidence; never qualify actual retirement or complete parent source."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13916-morning-completion-boundaries-public-v1'
scan.BEFORE = 'a23565cdc1888e37c1df951fbde9af80f30b03d6'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/architecture/MorningCompletionBoundaryCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
