"""Publish exact original whole20 data-envelope evidence, with actual/held scope separation."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13908-morning-data-envelopes-public-v1'
scan.BEFORE = 'f577edc11bd9f58d64bd6ea0658cb0868220d290'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/architecture/MorningDataEnvelopeCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
