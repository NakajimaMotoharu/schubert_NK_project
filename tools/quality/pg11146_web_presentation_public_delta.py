"""Save explicitly named public presentation proof changes; exclude held files before reads."""
import pg10606_fixed_error_public_delta as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11146-web-presentation-public-delta-v1'
scan.BEFORE='e8b02d5df2414fbad91be249f8eb3116108d5add'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg111',
    'tools/quality/architecture/WebPresentationFixtureJunitLauncher.java')

if __name__=='__main__':
    scan.main()
