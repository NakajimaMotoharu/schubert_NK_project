"""Immutable proper-stop source for captured current769 four-owned generation."""
import hashlib
import json
from pg1253_fresh_owned_stop_sources_v2 import sources as previous
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST
from pg1247_fresh_owned_stop_sources import W

BEFORE='8e5e15d65b69a5ca28cee870eed0c71969e36545d34b237a19cfd5a845f8db91'
GUEST_BEFORE='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/published-completed-capture-v2/before.private.json'
OWNED={'caddy.service':('811700','ab9156db01204f128fba490163785bef'),
       'schubert-nk-web.service':('809511','588c880aed434af6a6bb89c7ad3bf076'),
       'schubert-nk-api.service':('808288','0d384fd8429449a4957538aedcece601'),
       'artemis.service':('715021','1e638b051f644578ac4d6459e6845fbb')}
CHANGES=[('Pg1253','Pg1328'),('PG1253','PG1328'),('pg1253','pg1328'),
 ('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE),
 ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',DIGEST),('PG1068','PG1292'),('pg1068','pg1292'),
 ('28801629bec559edc757ef5df9c50b66fc524d898c1bca0a34f6015dd15f7218',BEFORE),
 ('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/fresh-completed-capture-v3/before.private.json',GUEST_BEFORE),
 ('2914e843f73d48dd93198dbdcae0f735','400b2e34105149ff8f3a11c21da0be6a'),('61234139496','73654946447'),('62400649336','75132489604'),('63034139496','75454946447'),
 ('9f651096-aef9-4fba-90b0-a653e99f035a','d2e3a86f-27a4-4c2a-be21-b512eebf1216'),
 ('2026-10-10T20:03:22.718197Z','2026-10-10T23:30:23.481632Z'),('2026-10-10T20:03:22.718197+00:00','2026-10-10T23:30:23.481632+00:00'),
 ('27accac0-c118-4c98-9244-02625a2d88a7','841b507c-2713-4ffe-8882-68f5fb3f87f5'),
 ('2026-10-10T20:22:34.439375Z','2026-10-10T23:54:39.918039Z'),("'100948'","'120359'"),('580631','702983'),
 ('672790','811700'),('ea56ffeed963402d8ff67a43b33ea123','ab9156db01204f128fba490163785bef'),
 ('670731','809511'),('4236e5a9bfd94fe09ca34323687bc5c3','588c880aed434af6a6bb89c7ad3bf076'),
 ('669495','808288'),('e5406d7517cc40958fdcf68008d23f23','0d384fd8429449a4957538aedcece601'),
 ('606091','715021'),('a1f58ea9067d4ebb815d73a783f109e2','1e638b051f644578ac4d6459e6845fbb')]


def sources():
    capture=json.loads((W/'pg1327-published-completed-capture-v2.safe.json').read_bytes())
    receipt=json.loads((W/'pg1322-published-root-done-receipt-v1.safe.json').read_bytes())
    if capture['actualExit']!=0 or capture['privateBeforeSha256']!=BEFORE or receipt['actualExit']!=0 or receipt['source']!=SOURCE or receipt['receipt']['endMonotonicUs']!=75132489604 or receipt['doneSha256']!='59f3b40104a9ea940779caac6aad6be6873e87f465a626e6f7860833c02d70a2':
        raise ValueError('actual current fullseal/genuine DONE required')
    result={}
    for name,text in previous().items():
        for old,new in CHANGES:text=text.replace(old,new)
        name=name.replace('1253','1328')
        if name.endswith('.py'):compile(text,'<actual current-owned full stop closure>','exec')
        result[name]=text
    return result
