"""Independent3657 XML/static/source qualification, no selected count summation."""
import inspect
import pg2579_current_jdbc_group_full_qualified as previous
from pg2600_retention_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG2578', 'PG2600').replace('3653', '3657').replace(
        "'batch':(1256,172,568)", "'batch':(1260,172,568)")
    compile(raw, '<independent retention full qualifier>', 'exec')
    return raw


def main():
    engine = previous.engine
    raw = inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1', 'pg2601-retention-group-full-qualified-v1').replace(
        'pg1532-server-six-v1', 'pg2600-server-six-v1').replace('PG1532', 'PG2600').replace(
        '4d6bcbddb417b76d27e52d5d9640752c300edccf', SOURCE)
    marker = "subprocess.check_output(['git', 'diff', '" + SOURCE + "', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(marker) != 1:
        raise ValueError('one provenance boundary required')
    raw = raw.replace(marker, "qualified_snapshot(root,begun['snapshot'])")
    def qualified_snapshot(root, snapshot):
        validate(snapshot)
        return False
    ns = {**engine.__dict__, 'CODE': server(), 'qualified_snapshot': qualified_snapshot}
    exec(compile(raw, '<independent full3657 qualifier>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
