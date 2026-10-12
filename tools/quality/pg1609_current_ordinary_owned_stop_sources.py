"""Generation-bound qualified stop ABI for actual PG1600 ordinary Root DONE."""
import json
from pg1579_current_owned_stop_sources import sources as previous,SOURCE
from pg1446_current_cold_stage import W

BEFORE='a600bb706bbd48168cd59b7028ec39b1f16464620d7fe26c4680e8dc136d5e27'
TOOLS='pg1609-current-ordinary-owned-stop-tools-v1'
CHANGES=[('1579','1609'),('pg1578-current-completed-seal-v1','pg1608-current-observation-full-seal-v3'),('52faff7f880f73f6020ac40d7aa1d8fe170e0e3ed6dfd7f10fd7fbddd8c4f9a9',BEFORE),('c52c914a72804a89b0fd5f252f6ac0fc','e4d891c38dde4e16a5c848e23ef3f83c'),("'50856'","'71184'"),('32043431270','38365395523'),('33583425972','39951854181'),('33843431270','40165395523'),('15700a87-9117-4f63-a0ff-768dd604d0f1','0be226b1-bbb7-43d3-aa9e-59d0bda70f9a'),('2026-10-11T21:18:59.040097Z','2026-10-12T06:23:13.176261Z'),('2026-10-11T21:18:59.040097+00:00','2026-10-12T06:23:13.176261+00:00'),('9e706936-a3c9-4a09-bb66-e2b1e8bbef66','d28eead2-941c-4b97-9747-1758c0809e29'),('2026-10-12T05:02:52.617413Z','2026-10-12T06:48:58.973359Z'),('108847','204695'),('161708','259611'),('b62723b53ece4420b783a627e3548012','99a144b6cba34d9e8ebdbfad060302de'),('159826','257744'),('fb683eeb6d3b4e90b66c1576f9108a0c','7a75a61efae5403692eb523eea322c19'),('158794','256734'),('2111873a431743359c0627a8f5e394c8','994fd53232ee426d9ca93a2f311bda53'),('118964','216143'),('6e745372ba4e4c7683cda767c607b93c','db75a3f0c2494fdea570b30012a5b871')]

def bind(raw):
    for old,new in CHANGES:raw=raw.replace(old,new)
    raw=raw.replace('pg1609-current-owned-stop-tools-v1',TOOLS)
    return raw

def sources():
    seal=json.loads((W/'pg1608-current-observation-full-seal-v3/manifest.safe.json').read_bytes())
    done=json.loads((W/'pg1601-current-newrun-done-receipt-v1.safe.json').read_bytes())
    if seal['actualExit']!=0 or seal['privateBeforeSha256']!=BEFORE or not seal['sqlOracleQualified']or done['actualExit']!=0 or done['source']!=SOURCE or done['receipt']['endMonotonicUs']!=39951854181:raise ValueError('current ordinary independent DONE and fullseal required')
    result={}
    for name,raw in previous().items():
        name=name.replace('1579','1609');raw=bind(raw)
        if any(s in raw for s in ['108847','158794','159826','161708','118964','15700a87-9117-4f63-a0ff-768dd604d0f1','33583425972','32043431270']):raise ValueError('old resume authority survived ordinary binding')
        if name.endswith('.py'):compile(raw,'<current ordinary stop ABI>','exec')
        result[name]=raw
    return result
