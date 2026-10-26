"""Exact four Test sources, three same-value/rename changes since Main type baseline."""
import pg10596_fixed_error_oracle_static as stage

if __name__ == '__main__':
    stage.SLOT = stage.data.ROOT.parent/'pgpt-runs/PG379/pg10630-query-semantic-constant-static-v1'
    stage.OUT = stage.data.BASE/'PG10630-query-semantic-constant-static-v1'
    stage.main()
