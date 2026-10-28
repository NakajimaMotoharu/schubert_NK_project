"""Explicit public static-review delta, never content-read held files."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13050-reference-identity-public-v1'
    scan.BEFORE = '45aef62bb229aad51935f29795160b06e8f89c59'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg130')
    scan.main()
