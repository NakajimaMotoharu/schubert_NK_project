"""Fresh one-use new-source ordinary admission; old a9 native saved, never credited."""
import inspect
import json
import subprocess

import pg2178_newsource_noargs_once as transport
import pg2684_operation_current_noargs_once as old
import pg3458_current_outbox_publication_post as post
from pg3462_outbox_current_observer import namespace, SOURCE, BOM
from pg1446_current_cold_stage import W

SLOT = 'pg3464-outbox-current-noargs-once-v1'


def native_physical_count():
    proof = json.loads((W / 'pg3430-current-a9-readonly-before-v1/manifest.safe.json').read_bytes())
    if (proof['actualExit'] != 0 or proof['productionSource'] != post.role.CURRENT
            or not proof['nativeMetadataStableTwice'] or proof['nativePhysicalFiles'] != 22):
        raise ValueError('actual preserved a9 native physical22 metadata witness required')
    return 22


def body():
    raw = old.body(BOM)
    for a, b in [('pg2682', 'pg3462'), (old.SLOT, SLOT), (old.SOURCE, SOURCE),
                 ('PG2654', 'PG3420'),
                 ('require(len(records)==28)', 'require(len(records)==' + str(native_physical_count()) + ')')]:
        if a not in raw:
            raise ValueError('complete new ordinary admission role: ' + a)
        raw = raw.replace(a, b)
    return raw


def payload(hashes):
    raw = inspect.getsource(transport.payload).replace('pg2174-normal-publication-full-post-v1', post.SLOT)
    ns = {**transport.__dict__, 'full_post': post.payload, 'body': body}
    exec(compile(raw, '<actual current4856 full independent admission projection>', 'exec'), ns)
    raw = ns['payload'](hashes)
    marker = "    after={**after,'native':native}\n"
    if raw.count(marker) != 1:
        raise ValueError('one old native-preservation boundary before new admission')
    # Projection truncates the independent reader's final save section. Retain
    # its actual native equality before copying old evidence or reserving start.
    return raw.replace(marker, "    require(native==historical_native)\n" + marker)


def main():
    if subprocess.check_output(['git', 'diff', '--name-only', SOURCE, 'HEAD', '--', 'src', 'pom.xml',
                                'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('same whole-qualified source required, never new Main during admission')
    raw = inspect.getsource(transport.main)
    for a, b in [('pg2176', 'pg3462'), ('pg2174-normal-publication-full-post-v1', post.SLOT)]:
        raw = raw.replace(a, b)
    ns = {**transport.__dict__, 'namespace': namespace, 'SOURCE': SOURCE, 'BOM': BOM,
          'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<new-source one durable noargs admission>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
