"""Both independent request-time and failed-pair metric contracts, whole65 suite."""
import pg3920_current_abandoned_boundary as selected
from pg1446_current_cold_stage import W

if __name__ == '__main__':
    selected.OUT = W / 'pg3924-current-failed-pair-boundary-v1'
    selected.SLOT = 'PG3924-candidate-v1'
    selected.LABEL = 'PG3924'
    selected.EXPECTED_TESTS = 65
    selected.EXTRA_METHODS = ['mdb3924001DifferentFailureMetricsCannotMintCanonicalFailedPairSnapshot']
    raise SystemExit(selected.main())
