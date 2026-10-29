"""Six source references only, retained raw diagnostics and unknown real close outcomes."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13972-main-resource-six-contracts-public-v1'
scan.BEFORE = '063fcb89711dd29238dd8a7549453d134a674bb5'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139','tools/quality/f03_remaining_main_resource_six_trace.py')

if __name__ == '__main__':scan.main()
