"""Fixed syscall-witness negative fixture; previous three cohorts preserved."""
import pg3218_legacy_negative_dispatch as dispatch
from pg1446_current_cold_stage import W


if __name__ == '__main__':
    dispatch.OUT = W / 'pg3230-legacy-negative-v1'
    dispatch.STAGE = '/home/ubuntu/pg3230-legacy-negative-v1'
    dispatch.FILES = ['pg3216_legacy_negative_observer.py', 'pg3218_legacy_negative_retained.py', 'pg3230_legacy_negative_syscalls.py']
    dispatch.ENTRY = 'pg3230_legacy_negative_syscalls.py'
    dispatch.main()
