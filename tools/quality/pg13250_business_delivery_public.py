"""Exact eight-Test/diagnostic supplement public delta; exclude held names before content access."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13250-business-delivery-public-v1'
    scan.BEFORE = 'be907c9f0b76e952e7f509a660867cc6cb18e60f'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg132')
    scan.main()
