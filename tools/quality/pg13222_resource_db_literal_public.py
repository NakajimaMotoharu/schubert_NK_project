"""Exact public finite-batch delta, all held paths excluded before any content read."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13222-resource-db-literal-public-v1'
    scan.BEFORE = '427cc1655866e654ce9a4e9a2ac3f707c6bfc883'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg132',
        'tools/quality/f03_literal_batch_sources.py','tools/quality/f03_literal_batch_preflight.py',
        'tools/quality/f03_literal_batch_diagnostic_v2.py','tools/quality/f03_literal_batch_quality.py','tools/quality/f03_literal_batch_trace.py')
    scan.main()
