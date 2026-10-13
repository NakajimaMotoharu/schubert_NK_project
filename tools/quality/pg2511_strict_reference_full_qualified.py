"""Independent fresh full3650 qualification; changed Main excludes old native import."""
import inspect
import pg1533_filesystem_full_qualification as engine
import pg2495_current_boundary_full_qualified as previous
from pg2510_strict_reference_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG2494', 'PG2510').replace('3649', '3650').replace(
        "'batch':(1252,172,568)", "'batch':(1253,172,568)").replace(previous.production(), SOURCE)
    marker = "'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class'})"
    if raw.count(marker) != 1:
        raise ValueError('exact previous physical-four class comparator required')
    raw = raw.replace(marker, "'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class',"
                      "'batch:dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence.class',"
                      "'batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.class',"
                      "'batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession$Session.class'})")
    raw = raw.replace("'semanticChangedClasses':3", "'semanticChangedClasses':6")
    compile(raw, '<PG2510 full candidate physical-seven qualifier>', 'exec')
    return raw


def main():
    raw = inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1', 'pg2511-strict-reference-full-qualified-v1').replace(
        'pg1532-server-six-v1', 'pg2510-server-six-v1').replace('PG1532', 'PG2510').replace(
        '4d6bcbddb417b76d27e52d5d9640752c300edccf', SOURCE)
    marker = "subprocess.check_output(['git', 'diff', '" + SOURCE + "', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(marker) != 1:
        raise ValueError('one exact frozen source provenance boundary required')
    raw = raw.replace(marker, "qualified_snapshot(root,begun['snapshot'])")
    def qualified_snapshot(root, snapshot):
        validate(snapshot)
        return False
    ns = {**engine.__dict__, 'CODE': server(), 'qualified_snapshot': qualified_snapshot}
    exec(compile(raw, '<PG2511 independent full qualifier>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
