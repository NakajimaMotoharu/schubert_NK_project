"""Public source-purpose review delta only; no held tool content."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13150-systemd-context-public-v1'
    scan.BEFORE = 'c0bda6487b09ea67924226ac0e9c25c147f476ca'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg131')
    scan.main()
