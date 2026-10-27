"""Explicit full-payload ownership PG/PT public delta only; no held content reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11394-full-payload-guard-public-v1'
scan.BEFORE='8dceb0101'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113',
    'tools/quality/architecture/FullPayloadGuardJunitLauncher.java',
    'tools/quality/architecture/FullPayloadGuardArtifactCoverageMeasure.java')
if __name__=='__main__':
    scan.main()
