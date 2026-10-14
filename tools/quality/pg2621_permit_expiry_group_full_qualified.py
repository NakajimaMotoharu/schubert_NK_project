"""Independent full3663 source/XML/physical/static qualification, not summed results."""
import inspect
import pg2601_retention_group_full_qualified as previous
from pg2620_permit_expiry_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG2600', 'PG2620').replace('3657', '3663').replace(
        "'batch':(1260,172,568)", "'batch':(1266,172,568)")
    compile(raw, '<independent full3663 qualifier>', 'exec')
    return raw


def main():
    engine = previous.previous.engine
    raw = inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1', 'pg2621-permit-expiry-group-full-qualified-v1').replace(
        'pg1532-server-six-v1', 'pg2620-server-six-v1').replace('PG1532', 'PG2620').replace(
        '4d6bcbddb417b76d27e52d5d9640752c300edccf', SOURCE)
    marker = "subprocess.check_output(['git', 'diff', '" + SOURCE + "', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(marker) != 1:
        raise ValueError('one source provenance boundary required')
    raw = raw.replace(marker, "qualified_snapshot(root,begun['snapshot'])")
    def qualified_snapshot(root, snapshot):
        validate(snapshot)
        return False
    ns = {**engine.__dict__, 'CODE': server(), 'qualified_snapshot': qualified_snapshot}
    exec(compile(raw, '<independent full3663 transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
