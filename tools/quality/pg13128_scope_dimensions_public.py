"""Explicit public tool delta; no held paths or private assets."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13128-scope-dimensions-public-v1'
    scan.BEFORE = '2e312c03b4d5843894e26c81d6b19d4f7e868c3a'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg131','tools/quality/quality_scope_dimensions.py')
    scan.main()
