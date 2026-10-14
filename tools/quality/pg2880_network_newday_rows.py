"""Independent all24 day15 normal steps/deletions/protectedInbox/HTTP post from sealed before."""
import inspect
import json
import pg1769_next_day_rows_oracle as prior
import pg2023_fresh_resume_rows_oracle as transport
from pg1446_current_cold_stage import W
from pg2862_network_newcurrent_observer import SOURCE

SLOT='pg2880-network-newday-rows-v1'


def oracle_source():
    raw=prior.oracle_source()
    old="r['business_date']=='2026-10-13'"
    if raw.count(old)!=1:raise ValueError('one fixed independent newday literal required')
    raw=raw.replace(old,"r['business_date']=='2026-10-15'")
    from pyflakes.api import check
    if check(raw,'<whole independent day15 rows oracle>'):raise ValueError('complete nextday oracle namespace required')
    compile(raw,'<all24 approved nextday postconditions>','exec');return raw


def payload():
    live=json.loads((W/'pg2874-network-newcurrent-live-binding-v1/manifest.safe.json').read_bytes())
    before=json.loads((W/'pg2876-network-admission-original-v2/manifest.safe.json').read_bytes())
    if live.get('actualExit')!=0 or before.get('actualExit')!=0 or before.get('productionSource')!=SOURCE:
        raise ValueError('actual source original and independent selectors required')
    binding=live['binding'];g=before['guest']
    raw=oracle_source()+'\nRUN='+repr(binding['run'])+'\nCUT='+repr(binding['cutoff'])+'\n'
    # Reuse the fixed readonly transport only, never old actual before/rows.
    body=prior.payload();body=body[body.index('import hashlib,os,pathlib,subprocess\n'):]
    body=body.replace('pg1759-next-day-ordinary-once-v1/before.private.json','pg2872-network-newcurrent-noargs-once-v2/external-before.private.json')
    body=body.replace('a919274268cfd66a4478f83cfeff52c1bfc3fb12323209133218bdc72d01c23e',g['privateBeforeSha256'])
    body=body.replace('pg1768-next-day-inbox-oracle-v1/oracle.private.json','pg2876-network-admission-original-v2/oracle.private.json')
    body=body.replace('a1f2ff92e014509b67dfb727f41fe5165b75d18f271ee90a68b8f7518aefe030',g['oracleSha256'])
    marker=';before=json.loads(br)'
    if body.count(marker)!=1:raise ValueError('one exact actual nested before rows required')
    body=body.replace(marker,";captured=json.loads(br);require(set(captured)=={'immutable','runtime','trees','observer'});before={'rows':captured['immutable']['rows']}")
    body=body.replace('pg1769-next-day-rows-oracle-v1',SLOT)
    raw+=body
    from pyflakes.api import check
    if check(raw,'<whole current day15 actual rows reader>'):raise ValueError('complete all24 newday reader namespace required')
    compile(raw,'<new logical day15 independent all24 rows>','exec');return raw


def main():
    raw=inspect.getsource(transport.main).replace('pg2021-fresh-resume-terminal-receipt-v1','pg2878-network-newcurrent-terminal-v1')
    ns={**transport.__dict__,'SLOT':SLOT,'SOURCE':SOURCE,'payload':payload}
    exec(compile(raw,'<current newday all24 independent dispatcher>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
