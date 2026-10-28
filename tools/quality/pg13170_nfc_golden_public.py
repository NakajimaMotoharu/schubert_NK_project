"""Explicit NFC Test/evidence public delta; held paths removed before content reads."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13170-nfc-golden-public-v1'
    scan.BEFORE = '844a1d298b2a883a5dd008bff920adf0a8d0e1f5'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg131',
        'tools/quality/architecture/NfcGoldenJunitLauncher.java','tools/quality/architecture/NfcGoldenArtifactCoverageMeasure.java')
    scan.main()
