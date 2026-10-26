"""Public final form lifecycle delta; subtract held paths before reading and preserve old failures."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '8efcc554c'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11026-form-lifecycle-public-v1'
    stage.PREFIXES += ('tools/quality/pg109','tools/quality/pg110','tools/quality/architecture/RemainingFormJunitLauncher.java')
    stage.main()
