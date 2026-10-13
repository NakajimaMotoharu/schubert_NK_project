"""BUG1204/YKT972: exact prior schema plus separately qualified native observation."""
import inspect
from pyflakes.api import check
import pg2060_fresh_runtime_retirement_independent_post as previous
original_payload=previous.payload
original_slot=previous.SLOT


def prior_equal(prior,before,after):
    return (type(prior)is dict and type(before)is dict and type(after)is dict
            and 'native'not in prior and set(before)==set(prior)|{'native'}
            and all(before[k]==v for k,v in prior.items())
            and type(before['native'])is dict and bool(before['native'])
            and before['native']==after.get('native'))


def payload(seals):
    raw=original_payload(seals).replace(original_slot,SLOT)
    old="and json.loads(prior_raw)==before)"
    if raw.count(old)!=1:raise ValueError('one prior schema comparison required')
    raw=raw.replace('runtime_contract={};exec(',inspect.getsource(prior_equal)+'\nruntime_contract={};exec(',1)
    raw=raw.replace(old,'and prior_equal(json.loads(prior_raw),before,after))')
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<actual native augmented retirement post>'):raise ValueError('complete actual globals required')
    compile(raw,'<native augmented retirement post>','exec');return raw


SLOT='pg2062-native-augmented-runtime-retirement-post-v1'


def main():
    previous.payload=payload
    previous.SLOT=SLOT
    return previous.main()


if __name__=='__main__':raise SystemExit(main())
