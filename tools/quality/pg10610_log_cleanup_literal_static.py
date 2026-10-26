"""Four explicit sources with two same-value changes; normal c919 Main type baseline only."""
import pg10596_fixed_error_oracle_static as stage

if __name__ == '__main__':
    stage.SLOT = stage.data.ROOT.parent/'pgpt-runs/PG379/pg10610-log-cleanup-literal-static-v1'
    stage.OUT = stage.data.BASE/'PG10610-log-cleanup-literal-static-v1'
    stage.main()
