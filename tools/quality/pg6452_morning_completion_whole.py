"""One grouped necessary4056 whole after Morning diagnostic and owner-list corrections."""
import inspect
import json
import subprocess
import pg6188_native_ownership_whole as base
from pg6450_morning_sequence_qualification import original_source

ROOT, W, BASE, sha = base.ROOT, base.W, base.BASE, base.sha
LABEL = 'PG6452'
SLOT = 'pg6452-morning-completion-six-v1'
QSHA = '8eb15b608718eb0f9eac4a92ccd03db4882a5436876d13c66563beedc3daf3c0'
ORDER_SHA = '25d0c5b2ccf61f4d25819b395342d96a389f35e1d1661a191a2290b714c65dfd'


def definitions():
    scope = {**vars(base), 'LABEL': LABEL, 'SLOT': SLOT, 'original_source': original_source,
        'prerequisites': prerequisites}
    for name in ('declared_inventory', 'server_source', 'driver_source', 'main'):
        raw = inspect.getsource(getattr(base, name))
        for before, after in (
            ('4023', '4056'), ('605', '610'), ('pg6188', 'pg6452'),
            ('SS313..317 ownership regression', 'Morning diagnostic326 and fixed-two-owner registration regression'),
            ('SSC317 unstarted management stop remains UNKNOWN.',
             'BUG1581 completion diagnostic cannot bypass retain;BUG1582 list capacity2 precedes both launch returns. '
             'Current original23 and raw all8511667 qualify the diagnostic code and fixed-two slots.')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<necessary4056 '+name+'>', 'exec'), scope)
    return scope


def declared_inventory(): return definitions()['declared_inventory']()
def server_source(head, digest): return definitions()['server_source'](head, digest)
def driver_source(fresh): return definitions()['driver_source'](fresh)


def prerequisites(source):
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator/proof first')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical original23 Main/Test/gates fixed')
    qp = BASE/'PG6450-morning-sequence-qualification-v1/manifest.json'
    op = BASE/'PG6446-sequence-capacity-current-v1/manifest.json'
    if sha(qp) != QSHA or sha(op) != ORDER_SHA:
        raise ValueError('exact genuine current23 and fixed-two/diagnostic JVM proof first')
    q, order = [json.loads(p.read_bytes()) for p in (qp, op)]
    if not (q['actualExit'] == order['actualExit'] == 0 and q['source'] == order['source'] == source
            and (q['tests'], q['suites'], q['physicalMain']) == (23, 10, 1667)
            and order['qualificationSha256'] == QSHA and order['order']['capacity'] == order['order']['maximumAdds'] == 2
            and order['diagnosticReauthentication']['allOuterMethodsExceptSequenceEquivalent']
            and len(order['diagnosticReauthentication']['actualCurrentCaseRefs']) == 2
            and order['diagnosticReauthentication']['priorPtOrNativeSuccessImported'] is False):
        raise ValueError('current diagnostic case XML/code identity and bounded registration, not native proof')
    private = W/'pg6450-morning-sequence-qualification-v1/manifest.safe.json'
    if sha(private) != q['privateManifestSha256']:
        raise ValueError('original all8511667 map')
    proof = json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    declared_inventory()


def main(): return definitions()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
