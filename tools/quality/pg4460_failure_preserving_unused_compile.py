"""Preserve first phase failure; qualify complete graph only after actual success."""
import inspect
import pg4456_inspectable_unused_compile as previous
from pg4444_failed_current_unused_sources import once


def compiler():
    raw = previous.compiler().replace('pg4456-', 'pg4460-').replace('PG4456', 'PG4460')
    raw = once(raw, '    validate_actual_graph(TARGET,hashes)', '    if r.returncode == 0:\n        validate_actual_graph(TARGET,hashes)')
    raw = once(raw, "value = {'actualExit': r.returncode,", "value = {'actualExit': r.returncode, 'completeGraphQualified': r.returncode == 0,")
    return raw


def main():
    namespace = {**vars(previous), 'compiler':compiler, '__file__':__file__}
    exec(compile(inspect.getsource(previous.main), '<newv4 first-result-preserving host compile>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
