"""One necessary grouped4064 whole for SSC327 Web PG plus deterministic NIO Test; not replay."""
import inspect
import json
import subprocess
import pg6188_native_ownership_whole as base
from pg6500_web_owned_component_qualification_v5 import original_source

ROOT, W, BASE, sha = base.ROOT, base.W, base.BASE, base.sha
LABEL = 'PG6490'
SLOT = 'pg6490-web-component-six-v1'
QSHA = None  # Must be replaced by genuine original27 qualification, never a predicted success.
ORDER_SHA = None


def definitions():
    scope = {**vars(base), 'LABEL': LABEL, 'SLOT': SLOT, 'original_source': original_source,
        'prerequisites': prerequisites}
    for name in ('declared_inventory', 'server_source', 'driver_source', 'main'):
        raw = inspect.getsource(getattr(base, name))
        for before, after in (
            ('4023', '4064'), ('605', '612'), ('pg6188', 'pg6490'),
            ('SS313..317 ownership regression', 'SSC327 ordinary Web internal IO binding and deterministic NIO collision regression'),
            ('SSC317 unstarted management stop remains UNKNOWN.',
             'SSC327 keeps the fixed Production five-argument/default IO bindings and tests actual self-owned DB/JMS/HTTP/FD lifecycle. '
             'Fresh27 includes seven component cases and one deterministic NIO collision; JVM owner-lock/volatile/default binding proof first.'),
            ('Original59 all-six qualification', 'Original27 all-six three-phase qualification')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<necessary4064 '+name+'>', 'exec'), scope)
    return scope


def declared_inventory(): return definitions()['declared_inventory']()
def server_source(head, digest): return definitions()['server_source'](head, digest)
def driver_source(fresh): return definitions()['driver_source'](fresh)


def prerequisites(source):
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator/proof first')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical original27 Main/Test/gates fixed')
    qp = BASE/'PG6500-web-owned-component-qualification-v5/manifest.json'
    op = BASE/'PG6484-web-owned-runtime-order-v1/manifest.json'
    if QSHA is None or ORDER_SHA is None or sha(qp) != QSHA or sha(op) != ORDER_SHA:
        raise ValueError('exact genuine current27 and JVM/default binding proof first')
    q, order = [json.loads(p.read_bytes()) for p in (qp, op)]
    if not (q['actualExit'] == order['actualExit'] == 0 and q['source'] == order['source'] == source
            and (q['tests'], q['suites'], q['physicalMain']) == (27, 11, 1667)
            and order['qualificationSha256'] == QSHA and order['soleProductionDefaultCaller']
            and order['structure']['fiveVolatileFlagsPreserved'] and order['structure']['privateFinalOwnerLock']
            and order['structure']['fixedDefaultFourBindings'] and len(order['actualCaseRefs']) == 7
            and order['nativeRootOrAuthorizationProven'] is False):
        raise ValueError('current seven actual XML cases/JVM/default bindings; not native proof')
    private = W/'pg6500-web-owned-component-qualification-v5/manifest.safe.json'
    if sha(private) != q['privateManifestSha256']:
        raise ValueError('original all8511667 map')
    proof = json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    declared_inventory()


def main(): return definitions()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
