"""Linux proc ENOENT/ESRCH race is terminal only with current PID absent."""
import errno


def confirmed_absence(error, present):
    if not isinstance(error, OSError) or type(present) is not bool:
        raise ValueError('typed proc error and current presence required')
    return error.errno in (errno.ENOENT, errno.ESRCH) and not present
