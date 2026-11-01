"""Exact in-memory credential value20 evidence; no ephemeral random material or real secrets saved."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17230-bootstrap-credential-values-public-save-v1'
save.BEFORE = '034827e5cedb1eac3df5dc34fbfa0c7bb681446b'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17216_', 'tools/quality/pg17218_', 'tools/quality/pg17220_', 'tools/quality/pg17221_', 'tools/quality/pg17222_', 'tools/quality/pg17224_', 'tools/quality/pg17226_', 'tools/quality/pg17228_', 'tools/quality/pg17230_', 'tools/quality/architecture/BootstrapCredentialValuesTwentyCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
