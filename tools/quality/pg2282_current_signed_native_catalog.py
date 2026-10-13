"""Same current Root native points, bound to corrected signed-current owned stop."""
import inspect
import json
import pg2254_newboot_native_catalog as prior
from pg2274_current_signed_owned_sources import TOOLS,SOURCE
from pg1446_current_cold_stage import W

SLOT='pg2282-current-signed-native-catalog-v1'


def catalog_source(receipt,binding,end):
    raw=prior.catalog_source(receipt,binding,end)
    return raw.replace('pg2246','pg2274').replace('Pg2246','Pg2274').replace('PG2246','PG2274')


def main():
    live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2234-newboot-fresh-day-terminal-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or term['actualExit']!=0:raise ValueError('same actual current terminal required')
    raw=inspect.getsource(prior.transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg2280-current-signed-owned-post-v1').replace('pg2030_parent_receipt.py','pg2274_parent_receipt.py')
    ns={**prior.transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<corrected native catalog entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
