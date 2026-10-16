"""New-only v3 closed18, same compiled artifact for inspect then place."""
import inspect
import pg4446_failed_current_unused_compile as previous
import pg4454_inspectable_failed_unused_sources as role

TARGET = role.W / role.TOOLS
ARCHIVE = previous.ARCHIVE.parent / role.ARCHIVE


def compiler():
    return role.role_text(previous.compiler()).replace('pg4446-', 'pg4456-').replace('PG4446', 'PG4456')


def main():
    namespace = {**vars(previous), 'role':role, 'TARGET':TARGET, 'ARCHIVE':ARCHIVE, 'compiler':compiler, '__file__':__file__}
    # validate_actual_graph uses an identical basename contract and only the new
    # fixed archive path; no graph membership/import allowlist relaxation.
    source = inspect.getsource(previous.validate_actual_graph)
    exec(compile(source, '<same graph newv3 archive>', 'exec'), namespace)
    exec(compile(inspect.getsource(previous.main), '<host-only closed inspectable18>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
