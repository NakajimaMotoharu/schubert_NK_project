"""BUG1328 corrected new-only run; PG3920 failed compiler receipt remains immutable."""
import pg3920_current_abandoned_boundary as selected
from pg1446_current_cold_stage import W

if __name__ == '__main__':
    selected.OUT = W / 'pg3922-current-abandoned-boundary-v1'
    selected.SLOT = 'PG3922-candidate-v1'
    selected.LABEL = 'PG3922'
    raise SystemExit(selected.main())
