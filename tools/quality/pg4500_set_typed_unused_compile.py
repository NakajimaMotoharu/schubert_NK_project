"""New-only v5 host compile; all closed graph/first-failure guards unchanged."""
import inspect
import pg4460_failure_preserving_unused_compile as previous
import pg4446_failed_current_unused_compile as base
import pg4498_set_typed_unused_sources as role

TARGET=role.W/role.TOOLS
ARCHIVE=base.ARCHIVE.parent/role.ARCHIVE


def compiler():
    return role.role_text(previous.compiler()).replace('pg4460-','pg4500-').replace('PG4460','PG4500')


def main():
    namespace={**vars(base),'role':role,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'compiler':compiler,'__file__':__file__}
    exec(compile(inspect.getsource(base.validate_actual_graph),'<same closed graph v5>','exec'),namespace)
    exec(compile(inspect.getsource(base.main),'<new v5 host compile>','exec'),namespace);return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
