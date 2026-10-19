"""Independent current0ea same-day applicability; no DB or clock mutation."""
import types
from pyflakes.api import check
import pg5020_current_query_oracle_preflight as previous
import pg5632_new_current_readonly as current
from pg4996_resume_connection import authenticate_host

SLOT='pg5636-same-day-query-preflight-v2'


def payload():
    raw=previous.payload();old=previous.current
    for before,after in((old.AFTER,current.AFTER),(old.context(),current.context()),(old.BOM,current.BOM)):
        if raw.count(before)!=1:raise ValueError('one exact current0ea before/oracle binding')
        raw=raw.replace(before,after,1)
    marker='now+datetime.timedelta(hours=2)'
    if raw.count(marker)!=1:raise ValueError('one independent upper window')
    raw=raw.replace(marker,'now+datetime.timedelta(minutes=35)',1)
    marker="\n  history={step:[r for r in before[BATCH]if r['step']==step and r['business_date']==day]for step in STEPS}"
    if raw.count(marker)!=1:raise ValueError('one same-day history projection')
    raw=raw.replace(marker,"\n  require(day==now.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat())"+marker,1)
    if check(raw,'<actual0ea independent same-day applicability>'):raise ValueError('complete emitted static0')
    compile(raw,'<no Root/clock/DB mutation>','exec');return raw


def main():
    authenticate_host();transport=previous.previous.previous.transport
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':current.SOURCE})(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
