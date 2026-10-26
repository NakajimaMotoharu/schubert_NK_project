"""Public declaration-only reconciliation delta, excluding held paths before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'ca907d44aff5de4912729b1aa060905b9bcb1f61'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10944-cross-owner-public-v1'
    stage.PREFIXES += ('tools/quality/pg109',)
    stage.main()
