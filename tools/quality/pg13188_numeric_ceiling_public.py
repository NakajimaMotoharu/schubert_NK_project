"""Explicit public numeric-boundary delta; exclude held paths before reading content."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13188-numeric-ceiling-public-v1'
    scan.BEFORE = 'e132023f28f87c87a81b1a6d1a653e29d4e4dd9d'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg131','tools/quality/architecture/FieldCodecCeilingJunitLauncher.java')
    scan.main()
