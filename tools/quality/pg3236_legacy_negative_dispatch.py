"""Actual FFI read-path qualification; previous failed/native cohorts retained."""
import pg3218_legacy_negative_dispatch as dispatch
from pg1446_current_cold_stage import W


if __name__ == '__main__':
    dispatch.OUT = W / 'pg3236-legacy-negative-v1'
    dispatch.STAGE = '/home/ubuntu/pg3236-legacy-negative-v1'
    dispatch.FILES = ['pg3216_legacy_negative_observer.py', 'pg3218_legacy_negative_retained.py', 'pg3236_native_query_negative.py']
    dispatch.ENTRY = 'pg3236_native_query_negative.py'
    dispatch.main()
