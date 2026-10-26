"""Explicit Web boundary public artifacts; original selector excludes held paths before content reads."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '1c529b7f257ee5162dfa6d149a256d059a516eb1'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10908-web-boundary-public-delta-v1'
    stage.PREFIXES += ('tools/quality/pg108','tools/quality/pg109',
        'tools/quality/architecture/WebBoundaryJunitLauncher.java',
        'tools/quality/architecture/ScenarioBoundaryJunitLauncher.java')
    stage.main()
