"""Explicit Main literal PG delta, held paths removed before any content reads."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13146-main-literal-public-v1'
    scan.BEFORE = 'a3ab19249deb99af1cc513bbaa169aae21367622'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg131')
    scan.main()
