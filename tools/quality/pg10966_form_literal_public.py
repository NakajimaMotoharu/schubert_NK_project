"""Public form fixture PG/PT delta; held paths excluded before any content access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '604604d23'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10966-form-literal-public-v1'
    stage.PREFIXES += ('tools/quality/pg109','tools/quality/architecture/FormBoundaryJunitLauncher.java')
    stage.main()
