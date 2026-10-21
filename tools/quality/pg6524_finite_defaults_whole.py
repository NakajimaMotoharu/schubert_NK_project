"""One integrated Test-only4073 whole after three finite fixture groups, never old PASS addition."""
import inspect
import json
import subprocess
import pg6188_native_ownership_whole as base
from pg6520_maintenance_owner_selected import guard_source as selected_guard, SLOT as SELECTED

ROOT, W, BASE, sha = base.ROOT, base.W, base.BASE, base.sha
OLD = 'e45cfd31c8d610922f4e9432cc1cf11fa9b48338'
LABEL = 'PG6524'
SLOT = 'pg6524-finite-defaults-six-v1'
QSHA = 'f8944dbe60d775ee479169070d2e883a0a4d5aa8f05818f6f3dd51a254a97ae9'
TESTS = {
    'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceResourceRetentionTest.java',
    'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedCaddyIdentityTest.java',
    'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/MaintenanceOwnerCredentialReaderTest.java',
}


def original_source():
    source = json.loads((W/SELECTED/'begin.safe.json').read_bytes())['source']
    selected_guard(source)
    return source


def definitions():
    scope = {**vars(base), 'LABEL': LABEL, 'SLOT': SLOT,
             'original_source': original_source, 'prerequisites': prerequisites}
    for name in ('declared_inventory', 'server_source', 'driver_source', 'main'):
        raw = inspect.getsource(getattr(base, name))
        for before, after in (('4023', '4073'), ('605', '614'), ('pg6188', 'pg6524')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<integrated finite4073 '+name+'>', 'exec'), scope)
    return scope


def declared_inventory(): return definitions()['declared_inventory']()
def server_source(head, digest): return definitions()['server_source'](head, digest)


def driver_source(fresh):
    raw = definitions()['driver_source'](fresh)
    start = raw.index("'trigger': "); end = raw.index('}, sort_keys=True)', start)
    trigger = ('Necessary integrated new Testsource4073/614/1667 after three finite groups: '
        'diagnostic/observation3, fixed Caddy literal Query3, maintenance-owner own TempDir reader3. '
        'All851 Production Main and all1667 physical Main unchanged; all old Test bodies/oracles retained. '
        'All three selected originals qualified before this one new-only whole. Allsix format before '
        'any PT, own temporary DB/JMS/HTTP and finite child fixtures only. No VM/current/actual Root/'
        'failed-cohort/intent/permit/key action. Original4064 is historical, never added to nine PASS; '
        'same-source actual XML/coverage and independent all-byte reader required. Formal/native separate.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator first')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw',
                               'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('original selected Main/Test/gates fixed')
    qp = BASE/'PG6522-maintenance-owner-qualification-v1/manifest.json'
    if QSHA is None or sha(qp) != QSHA:
        raise ValueError('genuine current reader15 qualification required')
    q = json.loads(qp.read_bytes())
    private = W/'pg6522-maintenance-owner-qualification-v1/manifest.safe.json'
    if not (q['source'] == source and q['actualExit'] == 0 and not q['changedPhysical']
            and (q['tests'], q['suites'], q['physicalMain']) == (15, 8, 1667)
            and sha(private) == q['privateManifestSha256']):
        raise ValueError('actual selected15/8511667 original byte map')
    proof = json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 Main fixed')
    for name, digest, origin, path in (
        ('PG6514-finite-policy-qualification-v1', '2664499fdf336a41910917a9392091abc86bcc7ba4f2f081de0de7553c58db5f',
         'a03b6153469f3478ed3b40d2c82e3f89c4d221ab', 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceResourceRetentionTest.java'),
        ('PG6518-caddy-identity-qualification-v1', 'e4e52e91f76bbcd9110478341c46acc97a13c5bc892d56bc6175239ed42e2344',
         'c2486f0107633c2670da5ed68d244cc62349657a', 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedCaddyIdentityTest.java')):
        previous = BASE/name/'manifest.json'
        if sha(previous) != digest:
            raise ValueError('both earlier selected originals qualified')
        value = json.loads(previous.read_bytes())
        if value['source'] != origin or value['actualExit'] != 0 or subprocess.check_output(
                ['git', 'diff', origin, source, '--', path], cwd=ROOT):
            raise ValueError('earlier individual Test oracle bytes unchanged, not old result import')
    changes = set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines())
    if changes != TESTS:
        raise ValueError('only three independent Test paths, no Production change')
    path = next(p for p in TESTS if p.endswith('/ServiceResourceRetentionTest.java'))
    before = subprocess.check_output(['git', 'show', OLD+':'+path], cwd=ROOT, text=True)
    after = subprocess.check_output(['git', 'show', source+':'+path], cwd=ROOT, text=True)
    anchor = '  @Test\n  void hold316001NormalAndNullPortsNeverManufactureAnUnknownRelease()'
    if before.count(anchor) != 1 or after.count(anchor) != 1 or before.split(anchor)[1] != after.split(anchor)[1]:
        raise ValueError('all prior retention Test bodies/helper/oracles unchanged')
    declared_inventory()


def main():
    # The generated main calls the current trigger override rather than its historic default.
    scope = definitions(); scope['main'].__globals__['driver_source'] = driver_source
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
