"""Independent all XML/static/archive/current source qualification; no old native import."""
import inspect
import pg1533_filesystem_full_qualification as engine
import pg2301_jdbc_host_integration_qualified as previous
from pg2404_question_jdbc_full_six import validate, production


def server():
    raw = previous.server().replace('PG2300', 'PG2404').replace('3635','3637').replace(
        "'batch':(1238,172,568)", "'batch':(1240,172,568)").replace(previous.production(), production())
    compile(raw, '<grouped full3637 exact independent qualification>', 'exec')
    return raw


def main():
    raw = inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1','pg2405-question-jdbc-full-qualified-v1').replace(
        'pg1532-server-six-v1','pg2404-server-six-v1').replace('PG1532','PG2404').replace(
        '4d6bcbddb417b76d27e52d5d9640752c300edccf',production())
    marker = "subprocess.check_output(['git', 'diff', '"+production()+"', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(marker) != 1:
        raise ValueError('exact frozen source provenance boundary required')
    raw = raw.replace(marker, "qualified_snapshot(root,begun['snapshot'])")
    def qualified_snapshot(root, snapshot):
        validate(snapshot)
        return False
    namespace = {**engine.__dict__, 'CODE':server(), 'qualified_snapshot':qualified_snapshot}
    exec(compile(raw, '<full3637 independent provenance>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
