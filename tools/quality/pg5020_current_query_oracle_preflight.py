"""Before-only independent current oracle window; no DB/clock/Root mutation."""
import types
from pyflakes.api import check
import pg4898_current_query_oracle_preflight as previous
import pg5016_new_current_readonly as current
from pg4996_resume_connection import authenticate_host

SLOT = 'pg5020-current-query-oracle-preflight-v1'


def payload():
    raw = previous.payload()
    for a, b in [(previous.current.AFTER, current.AFTER),
                 (previous.current.context(), current.context()), (previous.current.BOM, current.BOM)]:
        if raw.count(a) != 1:
            raise ValueError('one exact current-before oracle boundary ' + a)
        raw = raw.replace(a, b, 1)
    if check(raw, '<actuala2ecc independent applicability>'):
        raise ValueError('complete emitted namespace static0')
    return raw


def main():
    authenticate_host()
    transport = previous.previous.transport
    execute = types.FunctionType(transport.execute.__code__, {**vars(transport), 'SOURCE': current.SOURCE})
    return execute(SLOT, payload(), 45)


if __name__ == '__main__':
    raise SystemExit(main())
