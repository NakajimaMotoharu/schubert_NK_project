"""New qualification for newday applicability dependency; old5026 proof preserved."""
import inspect
import pg5026_new_normal_root_qualification as previous


def main():
    ns = {**vars(previous), 'NAMES': previous.NAMES + ['pg5030_new_day_query_oracle.py',
          'pg5030_new_day_query_oracle_test.py', 'pg5032_new_day_query_preflight.py',
          'pg5034_newday_root_qualification.py']}
    raw = inspect.getsource(previous.main)
    marker = "'pg4216_same_peer_observer_manager_test']"
    if raw.count(marker) != 1:
        raise ValueError('one affected independent oracle suite boundary')
    raw = raw.replace(marker, "'pg4216_same_peer_observer_manager_test','pg5030_new_day_query_oracle_test']", 1)
    exec(compile(raw, '<newday fresh qualified ordinary Root>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
