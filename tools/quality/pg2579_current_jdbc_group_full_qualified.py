"""Independent full3653 XML/static/source qualification, never add selected counts."""
import inspect
import pg2511_strict_reference_full_qualified as previous
import pg1533_filesystem_full_qualification as engine
from pg2578_current_jdbc_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG2510', 'PG2578').replace('3650', '3653').replace(
        "'batch':(1253,172,568)", "'batch':(1256,172,568)")
    compile(raw, '<independent all3653 source XML and physical qualifier>', 'exec')
    return raw


def main():
    raw = inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1', 'pg2579-current-jdbc-group-full-qualified-v1').replace(
        'pg1532-server-six-v1', 'pg2578-server-six-v1').replace('PG1532', 'PG2578').replace(
        '4d6bcbddb417b76d27e52d5d9640752c300edccf', SOURCE)
    marker = "subprocess.check_output(['git', 'diff', '" + SOURCE + "', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(marker) != 1:
        raise ValueError('one frozen snapshot provenance boundary required')
    raw = raw.replace(marker, "qualified_snapshot(root,begun['snapshot'])")
    def qualified_snapshot(root, snapshot):
        validate(snapshot)
        return False
    ns = {**engine.__dict__, 'CODE': server(), 'qualified_snapshot': qualified_snapshot}
    exec(compile(raw, '<independent grouped full qualifier>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
