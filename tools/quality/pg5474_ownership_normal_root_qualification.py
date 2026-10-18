"""Freeze exact new296 Root/observer/oracle host bytes before the one allowed new start."""
import inspect
import pg5026_new_normal_root_qualification as previous
import pg5470_new_normal_root_once as entry
import pg5472_new_normal_live_binding as binding

NAMES=['pg5464_new_current_readonly.py','pg5466_new_current_same_peer_observer.py',
    'pg5468_new_day_query_preflight.py','pg5470_new_normal_root_once.py','pg5472_new_normal_live_binding.py',
    'pg5474_ownership_normal_root_qualification.py','pg5474_ownership_normal_root_test.py',
    'pg5460_ownership_publication_post.py','pg4996_resume_connection.py',
    'pg5030_new_day_query_oracle.py','pg5030_new_day_query_oracle_test.py']


def main():
    ns={**vars(previous),'NAMES':NAMES,'entry':entry,'binding':binding}
    raw=inspect.getsource(previous.main).replace('pg5026_new_normal_root_test','pg5474_ownership_normal_root_test')
    marker="'pg4216_same_peer_observer_manager_test']"
    if raw.count(marker)!=1:raise ValueError('one original same-peer + independent newday test boundary')
    raw=raw.replace(marker,"'pg4216_same_peer_observer_manager_test','pg5030_new_day_query_oracle_test']",1)
    exec(compile(raw,'<actual296 source-bound ordinary Root qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
