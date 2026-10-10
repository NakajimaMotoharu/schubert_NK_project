"""Fresh fixed owned-stop closure from immutable qualified ABI; no operations."""
import hashlib
import json
from pathlib import Path

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='d5b00104280028d9ea81b44c1d1c805f3c2861ed'
BEFORE='28801629bec559edc757ef5df9c50b66fc524d898c1bca0a34f6015dd15f7218'
GUEST_BEFORE='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/fresh-completed-capture-v3/before.private.json'
OWNED={'caddy.service':('672790','ea56ffeed963402d8ff67a43b33ea123'),'schubert-nk-web.service':('670731','4236e5a9bfd94fe09ca34323687bc5c3'),'schubert-nk-api.service':('669495','e5406d7517cc40958fdcf68008d23f23'),'artemis.service':('606091','a1f58ea9067d4ebb815d73a783f109e2')}
CHANGES=[
    ('Pg1216','Pg1247'),('PG1216','PG1247'),('pg1216','pg1247'),
    ('bc98f52bd67e7b32f54a85d55bf7d8ceb08b97ca6891d081d192d4a4afab935a',BEFORE),
    ('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/full32-stop-owner-handoff-v1/after.private.json',GUEST_BEFORE),
    ('a14cc600a4fd4f2e9d8c4731ad9d754b','2914e843f73d48dd93198dbdcae0f735'),
    ('51172132518','61234139496'),('52530445203','62400649336'),('52972132518','63034139496'),
    ('343a5a1b-d064-47d5-88c2-31c36d7ba7a4','9f651096-aef9-4fba-90b0-a653e99f035a'),
    ('2026-10-10T12:40:27.396847Z','2026-10-10T20:03:22.718197Z'),
    ('2026-10-10T12:40:27.396847+00:00','2026-10-10T20:03:22.718197+00:00'),
    ('ada3f7ff-8287-48d7-9ba9-5cce71f61bd3','27accac0-c118-4c98-9244-02625a2d88a7'),
    ("'81093'","'100948'"),('430851','580631'),
    ('528966','672790'),('1037150931c04cb6b64b249c0cf916c3','ea56ffeed963402d8ff67a43b33ea123'),
    ('526861','670731'),('898429f0e6a64d4fa7a6c07e4473fe8a','4236e5a9bfd94fe09ca34323687bc5c3'),
    ('525675','669495'),('bfae0cf915c74f7bbf35a7a1ec4f8cd9','e5406d7517cc40958fdcf68008d23f23'),
    ('441175','606091'),('c874395201b94ae7b144e3a6bb2d3b8e','a1f58ea9067d4ebb815d73a783f109e2'),
]

def sources():
    build=json.loads((W/'pg1217-frozen-v1.safe.json').read_bytes())
    capture=json.loads((W/'pg1246-fresh-completed-capture-v3.safe.json').read_bytes())
    receipt=json.loads((W/'pg1242-fresh-ordinary-done-receipt-v1.safe.json').read_bytes())
    if build['actualExit']!=0 or capture['actualExit']!=0 or receipt['actualExit']!=0 or capture['privateBeforeSha256']!=BEFORE or receipt['receipt']['endMonotonicUs']!=62400649336:
        raise ValueError('actual current fullseal and genuine receipt required')
    files={}
    for name,digest in build['fileHashes'].items():
        if not name.endswith(('.py','.java')):continue
        raw=(W/'pg1216-native-tools-v1'/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('immutable qualified source SHA refused')
        s=raw.decode()
        for old,new in CHANGES:s=s.replace(old,new)
        if name=='pg1216_native_refs.py':
            for old,new in [("prior['trees']['startup']","prior['startup']"),("prior['trees']['originals']","prior['durable']['originals']"),("prior['trees']['backup']","prior['durable']['backup']")]:
                if s.count(old)!=1:raise ValueError('fixed complete fresh snapshot schema join required')
                s=s.replace(old,new)
        newname=name.replace('1216','1247')
        if newname.endswith('.py'):compile(s,'<actual fresh fixed closure>','exec')
        files[newname]=s
    if set(files)!={'Pg1247NativeArgumentTest.java','Pg1247NativeStop.java','Pg1247StopLabelTest.java','pg1247_configuration.py','pg1247_configuration_capture.py','pg1247_durable.py','pg1247_native_owned_stop.py','pg1247_native_refs.py','pg1247_parent_receipt.py','pg1247_row_bound.py','pg1247_stable_journal.py','pg526_native_term_witness.py','pg526_term_witness.py'}:
        raise ValueError('exact qualified fixed source closure required')
    return files

if __name__=='__main__':
    print(json.dumps({'sources':sorted(sources()),'operations0':True}))
