"""Independent current0ea newday applicability; no DB or clock mutation."""
import types
from pyflakes.api import check
import pg5468_new_day_query_preflight as previous
import pg5632_new_current_readonly as current
from pg4996_resume_connection import authenticate_host

SLOT='pg5636-new-day-query-preflight-v1'


def payload():
    raw=previous.payload();old=previous.current
    for before,after in((old.AFTER,current.AFTER),(old.context(),current.context()),(old.BOM,current.BOM)):
        if raw.count(before)!=1:raise ValueError('one exact current0ea before/oracle binding')
        raw=raw.replace(before,after,1)
    if check(raw,'<actual0ea independent newday applicability>'):raise ValueError('complete emitted static0')
    compile(raw,'<no Root/clock/DB mutation>','exec');return raw


def main():
    authenticate_host();transport=previous.previous.previous.previous.previous.transport
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':current.SOURCE})(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
