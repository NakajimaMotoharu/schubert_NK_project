"""Readonly whole new-source seal; independently observed owned identities.

SS341/343/353, PT-OPS-1702. Same-source receipt and immutable start baseline;
no stop authority. Backup content/retention and native qualification separate.
"""
import inspect
import pg1608_current_observation_full_seal_v3 as prior
from pg1700_new_source_live_binding import SOURCE, DIGEST
from pg1701_new_source_done_receipt import payload as receipt

SLOT = 'pg1702-new-source-completed-seal-v1'
OBSERVE = r'''
OWNED={}
for name in ['artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
 observed=show(name);pid=observed['MainPID']
 require(pid.isdecimal()and int(pid)>1 and observed['InvocationID']and observed['ActiveState']=='active'and observed['SubState']=='running'and not observed['Job']and observed['ControlPID']=='0'and observed['Result']=='success')
 p=pathlib.Path('/proc')/pid;argv=(p/'cmdline').read_bytes();ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19])
 require((p/'cgroup').read_text()=='0::/system.slice/'+name+'\n')
 require(show(name)==observed and(p/'cmdline').read_bytes()==argv and int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks)
 OWNED[name]=(pid,observed['InvocationID'],ticks,hashlib.sha256(argv).hexdigest())
'''


def once(raw, old, new):
    if raw.count(old) != 1: raise ValueError('one actual full-seal boundary required')
    return raw.replace(old, new)


def payload():
    raw = prior.payload()
    legacy = prior.prior.prior.receipt()
    legacy = legacy[:legacy.index("private=Path('/var/lib/pgpt-s1-preservation/pg1601-current-newrun-done-receipt-v1')")]
    guard = receipt(); guard = guard[:guard.index("private=Path('/var/lib/pgpt-s1-preservation/pg1701-new-source-done-receipt-v1')")]
    raw = once(raw, 'GUARD='+repr(legacy), 'GUARD='+repr(guard))
    raw = once(raw, 'OWNED='+repr(prior.prior.prior.OWNED), 'OWNED={}')
    old_schema = "{'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'}"
    raw = once(raw, old_schema, "{'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'}")
    raw = once(raw, "before['oneTimeRuntime']=before['runtime']", "before['oneTimeRuntime']=before['runtime']\nold['unitFilesActual']=before['unitFilesActual']\n"+OBSERVE)
    for old, new in [
        ('pg1608-current-observation-full-seal-v3',SLOT),
        ('pg1596-current-ordinary-before-v1/before.private.json','pg1699-new-current-ordinary-once-v1/before.private.json'),
        ('6d144309d3294abb31440d523940bfd4275d3a99eab3e4ce8e0486f81a154bce','ef9ddffcf813c6e4f4b8bb6379c30e5e0d87503a4abaf46859976a32fa8bfecb'),
        ('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE),
        ('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c',DIGEST),
        ('0.1.0-PG1544','0.1.0-PG1638'),('pg1544-manifest.sig','pg1638-manifest.sig'),
        ('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','02e941b9-1c52-4018-a193-63dd00b269af'),
        ('2026-10-12T06:23:13.176261Z','2026-10-12T14:19:28.968927Z'),
        ('d28eead2-941c-4b97-9747-1758c0809e29','40da389f-23fc-4ad4-a71b-cf72a6bd5a62')]:
        if old not in raw: raise ValueError('new Source baseline join boundary absent')
        raw = raw.replace(old,new)
    raw = once(raw, "'currentFourOwnedLive':True", "'currentFourOwnedLive':True,'observedOwned':OWNED,'productionSource':SOURCE")
    compile(raw,'<new Source whole independent seal>','exec')
    return raw


def main():
    raw = inspect.getsource(prior.prior.prior.prior.main)
    raw = raw.replace('pg1578-current-completed-seal-v1',SLOT)
    raw = raw.replace('pg1577-current-root-done-receipt-v1','pg1701-new-source-done-receipt-v1')
    raw = raw.replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE)
    ns = {**prior.prior.prior.prior.__dict__, 'payload':payload}
    exec(compile(raw,'<same Source seal readonly transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__': raise SystemExit(main())
