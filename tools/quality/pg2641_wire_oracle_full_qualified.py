"""Independent all3664 XML/static/physical-source qualification, not summation."""
import inspect
import pg2621_permit_expiry_group_full_qualified as previous
import pg1533_filesystem_full_qualification as engine
from pg2640_wire_oracle_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG2620', 'PG2640').replace('3663', '3664').replace(
        "'protocol':(81,17,174)", "'protocol':(82,17,174)")
    if "'protocol':(82,17,174)" not in raw:
        raise ValueError('one exact independent Protocol82 expectation required')
    compile(raw, '<independent all3664 qualifier>', 'exec')
    return raw


def main():
    raw = inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1', 'pg2641-wire-oracle-full-qualified-v1').replace(
        'pg1532-server-six-v1', 'pg2640-server-six-v1').replace('PG1532', 'PG2640').replace(
        '4d6bcbddb417b76d27e52d5d9640752c300edccf', SOURCE)
    marker = "subprocess.check_output(['git', 'diff', '" + SOURCE + "', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(marker) != 1:
        raise ValueError('one source provenance boundary required')
    raw = raw.replace(marker, "qualified_snapshot(root,begun['snapshot'])")
    def qualified_snapshot(root, snapshot):
        validate(snapshot)
        return False
    ns = {**engine.__dict__, 'CODE': server(), 'qualified_snapshot': qualified_snapshot}
    exec(compile(raw, '<all3664 immutable qualification transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
