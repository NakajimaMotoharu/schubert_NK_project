"""Explicit PG-only literal delta; exclude both held paths before any content access."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13202-systemd-test-literal-public-v1'
    scan.BEFORE = '4c21935ffde59458d97ccff7df7dc8533763da06'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg131','tools/quality/pg132')
    scan.main()
