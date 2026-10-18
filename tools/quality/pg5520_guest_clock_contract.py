"""BUG1454 strict guest-clock capture contract, then unchanged independent finite24 oracle."""
import datetime
import json
from pathlib import Path
from pg3136_browser_rows_oracle import qualify

DOMAIN='guest-postgresql-realtime'
SOURCE='guest-postgresql.clock_timestamp'


def instant(value):
    if type(value)is not str:raise ValueError('typed independent clock string required')
    parsed=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    if parsed.tzinfo is None:raise ValueError('timezone-aware clock witness required')
    return parsed


def verify_context(context):
    if type(context)is not dict or set(context)!={'owner','lower','upper','clockDomain','lowerClock','upperClock'}:
        raise ValueError('captured guest context required; old host-only context cannot be repaired by rows')
    if type(context['owner'])is not int or context['owner']<=0 or context['clockDomain']!=DOMAIN:raise ValueError('actual owner and explicit guest clock domain required')
    clocks=[]
    for label in('lower','upper'):
        value=context[label+'Clock']
        keys={'clockSource','instant','hostStartNanos','hostEndNanos','hostBeforeUtc','hostAfterUtc'}
        if type(value)is not dict or set(value)!=keys or value['clockSource']!=SOURCE or value['instant']!=context[label]:
            raise ValueError('exact independently captured SQL clock identity/bound')
        start,end=value['hostStartNanos'],value['hostEndNanos']
        if type(start)is not int or type(end)is not int or not 0<=end-start<=30_000_000_000:raise ValueError('bounded monotonic clock acquisition required')
        if instant(value['hostBeforeUtc'])>instant(value['hostAfterUtc']):raise ValueError('host clock reversal unsupported')
        clocks.append(value)
    lower,upper=clocks
    if lower['hostEndNanos']>upper['hostStartNanos']or upper['hostEndNanos']-lower['hostStartNanos']>600_000_000_000:
        raise ValueError('ordered same-process monotonic Browser timeout bracket required')
    if instant(lower['hostAfterUtc'])>instant(upper['hostBeforeUtc']):raise ValueError('host wall order reversed')
    span=(instant(context['upper'])-instant(context['lower'])).total_seconds()
    if not 0<=span<=600:raise ValueError('guest wall reversal/excess window rejected')
    return{'guestClockWindowQualified':True,'clockDomain':DOMAIN,'guestWindowSeconds':span,
        'clockBoundsDerivedFromRows':False,'historicalWindowRewritten':False}


def main():
    import sys
    if len(sys.argv)!=4:raise ValueError('private before/after/captured guest context required')
    before,after,context=[json.loads(Path(name).read_bytes())for name in sys.argv[1:]]
    clock=verify_context(context)
    result=qualify(before,after,context['owner'],context['lower'],context['upper'])
    print(json.dumps({**result,**clock},sort_keys=True))


if __name__=='__main__':main()
