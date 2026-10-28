"""Exact six-source public PG delta with held paths subtracted before content reads."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13236-db-web-literal-public-v1'
    scan.BEFORE = '6e3e3afd4530c494c3dbac40d083735d0f1dca97'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg132','tools/quality/f03_literal_batch_diagnostic_v3.py',
        'tools/quality/f03_literal_batch_preflight_v2.py','tools/quality/f03_spotbugs_fresh.py')
    scan.main()
