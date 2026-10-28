"""Explicit public unknown propagation whole4 evidence, no global secret or native claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13744-artemis-unknown-public-v1'
scan.BEFORE = '3b42b0c4031903aebd5f1e9900d82216dc9e4cbb'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/architecture/ArtemisUnknownCurrentFourJunitLauncher.java')

if __name__ == '__main__':scan.main()
