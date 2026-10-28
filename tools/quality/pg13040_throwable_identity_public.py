"""Explicit public delta only; held files excluded by the original scanner."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13040-throwable-identity-public-v1'
    scan.BEFORE = '04adbb5745be6bbfc23872e2f1544ba064aff312'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg130','tools/quality/architecture/ThrowableIdentityTypeInspection.java')
    scan.main()
