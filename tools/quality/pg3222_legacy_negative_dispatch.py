"""Fixed new-only v3 negative cohort, old v2 retirement is separate and once."""
import pg3218_legacy_negative_dispatch as dispatch
from pg1446_current_cold_stage import W


if __name__ == '__main__':
    dispatch.OUT = W / 'pg3222-legacy-negative-v1'
    dispatch.STAGE = '/home/ubuntu/pg3222-legacy-negative-v1'
    dispatch.FILES = ['pg3216_legacy_negative_observer.py', 'pg3218_legacy_negative_retained.py', 'pg3222_legacy_negative_typed.py']
    dispatch.ENTRY = 'pg3222_legacy_negative_typed.py'
    dispatch.main()
