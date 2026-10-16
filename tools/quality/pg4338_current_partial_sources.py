"""SSC292 new-instance partial recovery. Frozen original58917 is never rewritten."""
import ast
import hashlib
import inspect
from pg4060_original_profile_dual_stack import once
from pg1446_current_cold_stage import W
import pg4164_retained_pair_profile as old_profile
import pg4168_retained_pair_keeper as old_keeper
import pg4132_signed_phase_invariant as signed
import pg4178_pool_bounds as pool
import pg4336_current_unknown_read as observed
import pg4324_current_failed_post as prepared_post
from pg782_owned_handoff import terminate

PARTIAL = 'pg4340-current-partial-v1'
POST = 'pg4342-current-partial-post-v1'
KEEPER = 'pg4344-current-pair-keeper-v1'
OBSERVED_SHA = '92bb9a17f47de3c2bcbee713e5e5e28cb7336702c0f2d4a5d9495fec3b9dcc5f'


def profile_source():
    raw = inspect.getsource(old_profile)
    bindings = [('790010', '815726'), ('789928', '815643'), ('14181503', '15409721'),
                ('14180650', '15408795'), ('789926', '815641'), ('session-921', 'session-970'),
                ('ed8889ef439ebe28100f5a4d4cee289004c55e9bfb108a7a314c37d25aaf7af2',
                 '5312514ace02eda3eb8f4f4941095f5e334dc00859d52aa2a5a811a626c7b698'),
                ('pg4146-complete-signed-owned-recovery-v1', 'pg4316-current-failed-dispatch-v1'),
                ('pg4112-canonical-epoch-owned-tools-v1', 'pg4312-current-failed-owned-tools-v1')]
    for old, new in bindings:
        if old not in raw:
            raise ValueError('explicit profile binding missing: ' + old)
        raw = raw.replace(old, new)
    return raw


def keeper():
    raw = observed.payload().split('\nimport time\nfolder=')[0]
    raw = once(raw, '(["inspect"],["recover"])', '(["proof"],["recover"])')
    raw = once(raw, "save=base/'" + observed.SLOT + "'", "save=base/('" + KEEPER + "-'+MODE)")
    # This diagnostic prelude's unused imports are not hidden from qualification.
    raw = once(raw, 'import base64,selectors', 'import base64')
    raw += '\nPROFILE_SOURCE=' + repr(profile_source()) + '\nSIGNED_SOURCE=' + repr(signed.source())
    raw += '\nPOOL_SOURCE=' + repr(inspect.getsource(pool)) + '\n' + inspect.getsource(terminate) + '\n'
    body = old_keeper.BODY
    for old, new in [('790010', '815726'), ('789928', '815643'), ('14181503', '15409721'),
                     ('14180650', '15408795'), ('pg4160-retained-config-read-v1', observed.SLOT),
                     ('e5fff095e3d770b128150029cefa2b3c501462d1e4f5b41279b5d80500be0d0b', OBSERVED_SHA),
                     ('SSC288', 'SSC292')]:
        body = body.replace(old, new)
    body = once(body, "expected=reference['current']", "expected=reference['samples'][-1]")
    body = once(body, "['units','actors','durable','native','startup','runtime']",
                "['units','actors','detailedActors','durable','native','startup','runtime']")
    return raw + body


def mismatch_source():
    return '''def same_values(before,after):
 keys=['units','actors','detailedActors','durable','native','startup','runtime']
 changed=[k for k in keys if before[k]!=after[k]]
 if before['database']['rows']!=after['database']['rows']:changed.append('databaseRows')
 if changed:
  # Preserve full rejected pair privately; never retry a stop or normalize it.
  save_private('rejected-pair.private.json',{'before':before,'after':after,'changedKeys':changed})
  raise ValueError('fresh snapshot pair differs; exact private pair preserved')
'''


def partial():
    raw = (W / 'pg4316-current-failed-dispatch-v1-artifact/dispatch.private.py').read_text()
    if hashlib.sha256(raw.encode()).hexdigest() != observed.PIN:
        raise ValueError('frozen original full driver first')
    raw = once(raw, "save=base/('pg4316-current-failed-dispatch-v1-'+MODE)",
               "save=base/('" + PARTIAL + "-'+MODE)")
    raw = once(raw, "EXPECTED_ACTORS=actor_certificate['second']['actors']",
               "EXPECTED_ACTORS={u:a for u,a in actor_certificate['second']['actors'].items()if u!='caddy.service'}")
    old = "captures={unit:show_terminal(unit)for unit in ORDER};durable_save('before.private.json',encode(baseline));durable_save('terminal-before.private.json',encode(captures))"
    new = """captures={unit:show_terminal(unit)for unit in ORDER}
 prior_raw=(base/'pg4336-current-unknown-read-v1/observed.private.json').read_bytes();require(hashlib.sha256(prior_raw).hexdigest()==OBSERVED_SHA)
 prior_caddy=json.loads(prior_raw)['caddyBefore']
 require(terminal_contract.normal_terminal(prior_caddy,captures['caddy.service']));terminal_contract.kernel_empty('caddy.service');require(not Path('/proc/808868').exists())
 captures['caddy.service']=prior_caddy
 durable_save('before.private.json',encode(baseline));durable_save('terminal-before.private.json',encode(captures))"""
    raw = once(raw, old, new)
    raw = 'OBSERVED_SHA=' + repr(OBSERVED_SHA) + '\n' + raw
    raw = once(raw, " def reserve(unit):durable_save(unit+'.stop-reserved.private',encode({'unit':unit,'before':captures[unit],'holderPid':owned[0],'holderTicks':holder_ticks}))",
               " def reserve(unit):\n  name=unit+('.prior-terminal-observed.private'if unit=='caddy.service'else'.stop-reserved.private')\n  durable_save(name,encode({'unit':unit,'before':captures[unit],'holderPid':owned[0],'holderTicks':holder_ticks,'newStopPermitted':unit!='caddy.service'}))")
    raw = once(raw, ' def stop(unit):\n  require(show_terminal(unit)==captures[unit]);holder()',
               " def stop(unit):\n  if unit=='caddy.service':\n   require(terminal_contract.normal_terminal(captures[unit],show_terminal(unit)));terminal_contract.kernel_empty(unit);require(not Path('/proc/808868').exists());holder();return\n  require(show_terminal(unit)==captures[unit]);holder()")
    raw = once(raw, "print('SSC291_STOPPED unit='+unit+' generationVerified=true',flush=True)",
               "print('SSC292_TERMINAL unit='+unit+' issued='+str(unit!='caddy.service').lower()+' generationVerified=true',flush=True)")
    raw = once(raw, "'recoverySixNormal':MODE=='recover'",
               "'recoverySixNormal':MODE=='recover','caddyPriorStopAuthenticated':True,'newStopCount':5 if MODE=='recover'else 0,'original58917Normal':False")
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'same_values')
    return once(raw, ast.get_source_segment(raw, node), mismatch_source().rstrip())


def post():
    raw = prepared_post.payload()
    raw = once(raw, "save=base/'pg4324-current-failed-independent-post-v1'", "save=base/'" + POST + "'")
    raw = once(raw, "RECOVERY='/var/lib/pgpt-s1-preservation/pg4316-current-failed-dispatch-v1-recover'",
               "RECOVERY='/var/lib/pgpt-s1-preservation/" + PARTIAL + "-recover'")
    return once(raw, "before['actors']==reference['actors']",
                "before['actors']=={u:a for u,a in reference['actors'].items()if u!='caddy.service'}")


def files():
    return {'keeper.py': keeper(), 'partial.py': partial(), 'post.py': post()}
