"""SS343/SSC124 corrected independent failed-projection expectation; prior failure retained."""
import pg3920_current_abandoned_boundary as selected
from pg1446_current_cold_stage import W

if __name__ == '__main__':
    selected.OUT = W / 'pg3926-current-failed-pair-boundary-v1'
    selected.SLOT = 'PG3926-candidate-v1'
    selected.LABEL = 'PG3926'
    selected.EXPECTED_TESTS = 65
    selected.EXTRA_METHODS = ['mdb3924001DifferentFailureMetricsCannotMintCanonicalFailedPairSnapshot']
    raise SystemExit(selected.main())
