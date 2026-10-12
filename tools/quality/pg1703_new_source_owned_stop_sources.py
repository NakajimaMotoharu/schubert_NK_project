"""Qualified stop ABI rebound only from independent actual2741 DONE/full seal."""
import json
import re
from pg1446_current_cold_stage import W
import pg1609_current_ordinary_owned_stop_sources as prior
from pg1700_new_source_live_binding import SOURCE, DIGEST

TOOLS='pg1703-new-source-owned-stop-tools-v1'


def context():
    seal=json.loads((W/'pg1702-new-source-completed-seal-v1/manifest.safe.json').read_bytes())
    done=json.loads((W/'pg1701-new-source-done-receipt-v1.safe.json').read_bytes())
    if (seal.get('actualExit')!=0 or seal.get('productionSource')!=SOURCE
            or seal.get('sqlOracleQualified')is not True or seal.get('currentFourOwnedLive')is not True
            or done.get('actualExit')!=0 or done.get('source')!=SOURCE):
        raise ValueError('sameSource genuine DONE and all-field seal required')
    digest=seal.get('privateBeforeSha256');owned=seal.get('observedOwned');receipt=done.get('receipt')
    if type(digest)is not str or re.fullmatch('[a-f0-9]{64}',digest)is None:
        raise ValueError('sealed before digest required')
    if type(owned)is not dict or set(owned)!={'caddy.service','schubert-nk-web.service','schubert-nk-api.service','artemis.service'}:
        raise ValueError('exact four observed role identities required')
    for identity in owned.values():
        if (type(identity)is not list or len(identity)!=4 or type(identity[0])is not str or not identity[0].isdigit()
                or int(identity[0])<=1 or type(identity[1])is not str or re.fullmatch('[a-f0-9]{32}',identity[1])is None
                or type(identity[2])is not int or identity[2]<=0 or type(identity[3])is not str
                or re.fullmatch('[a-f0-9]{64}',identity[3])is None):
            raise ValueError('complete actual actor identity required')
    if type(receipt)is not dict or type(receipt.get('endMonotonicUs'))is not int or not 66941284515<receipt['endMonotonicUs']<=68741284515:
        raise ValueError('actual genuine Root original budget required')
    if seal.get('genuineCompletion')!=receipt or type(seal.get('doneEndUtc'))is not str:
        raise ValueError('independently joined completion required')
    return digest,owned,receipt,seal['doneEndUtc']


def bind(raw):
    digest,owned,done,utc=context()
    pairs=[('pg1609', 'pg1703'),('Pg1609','Pg1703'),('PG1609','PG1703'),
           ('pg1703-current-ordinary-owned-stop-tools-v1',TOOLS),
           ('pg1608-current-observation-full-seal-v3','pg1702-new-source-completed-seal-v1'),
           (prior.BEFORE,digest),('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE),
           ('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c',DIGEST),
           ('PG1544','PG1638'),('pg1544','pg1638'),
           ('e4d891c38dde4e16a5c848e23ef3f83c','fe43e94b1fbf4886bb4ab3922fd16f9c'),
           ('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','02e941b9-1c52-4018-a193-63dd00b269af'),
           ('2026-10-12T06:23:13.176261Z','2026-10-12T14:19:28.968927Z'),
           ('2026-10-12T06:23:13.176261+00:00','2026-10-12T14:19:28.968927+00:00'),
           ('d28eead2-941c-4b97-9747-1758c0809e29','40da389f-23fc-4ad4-a71b-cf72a6bd5a62'),
           ('2026-10-12T06:48:58.973359Z',utc)]
    for unit,old in {'caddy.service':('259611','99a144b6cba34d9e8ebdbfad060302de'),
                     'schubert-nk-web.service':('257744','7a75a61efae5403692eb523eea322c19'),
                     'schubert-nk-api.service':('256734','994fd53232ee426d9ca93a2f311bda53'),
                     'artemis.service':('216143','db75a3f0c2494fdea570b30012a5b871')}.items():
        pairs.append((old[1],owned[unit][1]))
    for a,b in pairs:raw=raw.replace(a,b)
    numbers={'71184':'106924','38365395523':'66941284515','39951854181':str(done['endMonotonicUs']),
             '40165395523':'68741284515','204695':'302199','259611':owned['caddy.service'][0],
             '257744':owned['schubert-nk-web.service'][0],'256734':owned['schubert-nk-api.service'][0],
             '216143':owned['artemis.service'][0]}
    for a,b in numbers.items():raw=re.sub(r'\b'+a+r'\b',b,raw)
    return raw


def sources():
    result={}
    for name,raw in prior.sources().items():
        name=name.replace('1609','1703');raw=bind(raw)
        if any(v in raw for v in ['0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','e4d891c38dde4e16a5c848e23ef3f83c',
                                 'pg1609','Pg1609','38365395523','40165395523','0.1.0-PG1544']):
            raise ValueError('historical authority survived sameSource stop binding')
        if name.endswith('.py'):compile(raw,'<sameSource actual stop ABI>','exec')
        result[name]=raw
    return result
