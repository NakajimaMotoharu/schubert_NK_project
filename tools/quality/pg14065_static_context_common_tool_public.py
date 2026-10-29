"""Fresh public scan after precommit-only document whitespace repair."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14065-static-context-common-tool-public-v2'
scan.BEFORE = '50d1fe8ba40b7de94d5a5d10a8464a9fabbc0d71'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg140','tools/quality/static_context_reader_v1.py','tools/quality/static_context_post_v1.py','tools/quality/static_context_post_v2.py')

if __name__ == '__main__':scan.main()
