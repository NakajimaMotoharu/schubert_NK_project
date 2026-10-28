"""Bound public five-existing-reason metadata delta; no product actions or global scan claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13710-concurrency-reason-public-v1'
scan.BEFORE = '9f43e1a753ac2dd219e8b2441c86d04d9ca29731'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/f03_current_concurrency_trace.py')

if __name__ == '__main__':scan.main()
