"""BUG1383 corrected independent scope-frame oracle; new namespace, no failed replay."""
import types
from pyflakes.api import check
import pg4744_same_day_query_preflight as previous
import pg4250_current_admission_image as transport
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4750-scoped-query-preflight-v2'


def payload():
    raw=previous.payload()
    if check(raw,'<scoped query preflight>'):raise ValueError('complete emitted namespace')
    return raw


def main():
    authenticate_host()
    execute=types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':previous.current.SOURCE})
    return execute(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
