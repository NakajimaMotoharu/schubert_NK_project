"""Only the PG1381-proven retained child and parent, once each under fresh ten Ref."""
import ast
import pg1368_bootstrap_fixed_ref_handoff as previous
import pg1381_role_failed_ref_pair_proof as proof
from pg1334_published_owned_stop_sources_v2 import SOURCE

PROOF = 'ca3f18cc007730853643b7ae992b52925161c027f75f02dd3bd0cb29b39d5741'

def payload(seals):
    raw = previous.payload(seals)
    changes = (
        (previous.PROOF, PROOF),
        ('pg1367-bootstrap-failed-ref-pair-v1', 'pg1381-role-failed-ref-pair-v1'),
        ('pg1368-bootstrap-fixed-ref-handoff-v1', 'pg1382-role-fixed-ref-handoff-v1'),
        ('PG1368-bootstrap-fixed-ref-handoff-v1', 'PG1382-role-fixed-ref-handoff-v1'),
        ('PG1368_RECOVERY', 'PG1382_RECOVERY'),
        ('840449', '841734'), ('7784890', '8003102'),
        ('840478', '841763'), ('7785030', '8003222'),
        ('68233c1d4b72c68a283ab97cba70016fd72d3d4398cc163e117abba34e2a4a82',
         '59288d02dc262cc503775fc2202bca4dda052c5680629efe0ba606fc25a2182f'),
        ('501bccd8021ac84dc362ba34d63434491e200ff6d1ce184ccd49fa75dd49cb79',
         '12426413c4d6ce3d3dc0bf4335a62aadb4bb65fca17f9d56b78c1d8273ec48ed'),
        (':1.616878', ':1.616973'),
    )
    for old, new in changes:
        if old not in raw:
            raise ValueError('complete current actor binding required')
        raw = raw.replace(old, new)
    actual = proof.payload(seals)
    replacement = {n.name: ast.get_source_segment(actual, n)
                   for n in ast.parse(actual).body
                   if isinstance(n, ast.FunctionDef) and n.name in {'candidate', 'fixed_owner'}}
    parent = replacement['fixed_owner'].replace('def fixed_owner():', 'def parent_only():')
    start = parent.index(' kids='); end = parent.index(' q=', start)
    parent = parent[:start] + " require(not pathlib.Path('/proc/841763').exists()and all(not(t/'children').read_text().strip()for t in(p/'task').iterdir()))\n" + parent[end:]
    replacement['parent_only'] = parent.replace("'child':child", "'child':None")
    for n in reversed(ast.parse(raw).body):
        if isinstance(n, ast.FunctionDef) and n.name in replacement:
            lines = raw.splitlines(keepends=True)
            raw = ''.join(lines[:n.lineno-1]) + replacement[n.name] + '\n' + ''.join(lines[n.end_lineno:])
    compile(raw, '<exact current retained role pair recovery>', 'exec')
    return raw

def source():
    return proof.source().replace('pg1381-role-failed-ref-pair-v1', 'pg1382-role-fixed-ref-handoff-v1')

def main():
    env = dict(proof.previous.previous.previous.previous.prior.prior.previous.transport.__dict__,
               SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<role pair recovery transport>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
