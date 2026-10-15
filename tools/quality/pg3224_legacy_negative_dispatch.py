"""Known-partial v3 prepare completion and first actual v3 negative invocation."""
import pg3218_legacy_negative_dispatch as dispatch
from pg1446_current_cold_stage import W


if __name__ == '__main__':
    dispatch.OUT = W / 'pg3224-legacy-negative-v1'
    dispatch.STAGE = '/home/ubuntu/pg3224-legacy-negative-v1'
    dispatch.FILES = ['pg3216_legacy_negative_observer.py', 'pg3218_legacy_negative_retained.py', 'pg3224_negative_prepare_recovery.py']
    dispatch.ENTRY = 'pg3224_negative_prepare_recovery.py'
    dispatch.main()
