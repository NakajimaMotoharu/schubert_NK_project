"""Exact public RFC verification delta; held files excluded before content/metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16538-public-signature-public-save-v1'
save.BEFORE='70459982024f9b20196927386b41c4bbf9bd80e8'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16524_','tools/quality/pg16526_','tools/quality/pg16528_','tools/quality/pg16530_','tools/quality/pg16532_','tools/quality/pg16534_','tools/quality/pg16536_','tools/quality/pg16538_','tools/quality/architecture/ReleasePublicSignatureEightCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
