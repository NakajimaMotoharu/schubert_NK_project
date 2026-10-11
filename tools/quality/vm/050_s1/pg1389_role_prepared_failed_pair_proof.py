"""Current failed closed boundary: preserve actual prepared role, exact pair, full originals."""
import inspect
import pg1381_role_failed_ref_pair_proof as previous
import pg1369_bootstrap_role_policy as policy
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    raw=previous.payload(seals).replace('1374','1380')
    marker="require({x.name for x in root.iterdir()}=={'refs.private.log'})"
    if raw.count(marker)!=1:raise ValueError('one actual saved phase inventory required')
    raw=raw.replace(marker,"require({x.name for x in root.iterdir()}=={'refs.private.log','before.private.json','prepared.private.json'})")
    raw=raw.replace('bus=dbus.SystemBus(private=True);','import types\nrole_policy=types.ModuleType("independent_role_policy");exec('+repr(inspect.getsource(policy))+',role_policy.__dict__)\nbus=dbus.SystemBus(private=True);')
    marker=' owner=fixed_owner();native=snapshot();require(native==snapshot()and owner==fixed_owner())'
    if raw.count(marker)!=1:raise ValueError('one actual full failed owner/native scope required')
    raw=raw.replace(marker,marker+'''
 failed_root=base/'pg1380-bootstrap-role-prepare-v1'
 initial=json.loads(strict(failed_root/'before.private.json',0o600,67108864));prepared=json.loads(strict(failed_root/'prepared.private.json',0o600,67108864))
 require(initial['current']==prepared['current']==after and prepared['native']==native)
 original_raw=strict(base/'pg1344-current-bootstrap-before-v1/after.private.json',0o600,67108864)
 require(hashlib.sha256(original_raw).hexdigest()=='f64ed4689d2c52e2227f771f7870414686ff0e6f52a6dc7b3d1b22313668428d'and json.loads(original_raw)['native']==initial['native'])
 role_policy.delta(initial['native'],native,prepared['startNs'],prepared['endNs'])
 role=pathlib.Path(role_policy.ROOT,role_policy.ROLE);require(not list(role.iterdir())and not os.listxattr(role))
''')
    raw=raw.replace('pg1381-role-failed-ref-pair-v1','pg1389-role-prepared-failed-pair-v1').replace('PG1381-role-failed-ref-pair-v1','PG1389-role-prepared-failed-pair-v1')
    compile(raw,'<prepared closed-boundary failed exact pair>','exec');return raw

def main():
    env=dict(previous.previous.previous.previous.previous.prior.prior.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    raw=previous.source().replace('pg1381-role-failed-ref-pair-v1','pg1389-role-prepared-failed-pair-v1')
    exec(compile(raw,'<prepared role failed pair proof transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
