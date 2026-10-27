"""Save explicit public catalog/scalar/pool proof delta, held names excluded before reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11198-api-catalog-scalar-pool-public-delta-v1'
scan.BEFORE='18036a7e2'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg111',
    'tools/quality/architecture/CatalogScalarPoolFixtureJunitLauncher.java')
if __name__=='__main__':
    scan.main()
