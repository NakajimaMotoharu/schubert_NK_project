"""Freeze source-bound0ea observer/oracle/Root host bytes before one allowed start."""
import inspect
import pg5026_new_normal_root_qualification as previous
import pg5638_new_normal_root_once as entry
import pg5640_new_normal_live_binding as binding

NAMES=['pg5632_new_current_readonly.py','pg5634_new_current_same_peer_observer.py',
  'pg5636_new_day_query_preflight.py','pg5638_new_normal_root_once.py','pg5640_new_normal_live_binding.py',
  'pg5642_current_normal_root_qualification.py','pg5642_current_normal_root_test.py',
  'pg5630_current_publication_post.py','pg4996_resume_connection.py',
  'pg4742_same_day_query_oracle.py','pg4742_same_day_query_oracle_test.py']


def main():
    ns={**vars(previous),'NAMES':NAMES,'entry':entry,'binding':binding}
    raw=inspect.getsource(previous.main).replace('pg5026_new_normal_root_test','pg5642_current_normal_root_test')
    marker="'pg4216_same_peer_observer_manager_test']"
    if raw.count(marker)!=1:raise ValueError('one original same-peer/independentnewday test boundary')
    raw=raw.replace(marker,"'pg4216_same_peer_observer_manager_test','pg4742_same_day_query_oracle_test']",1)
    exec(compile(raw,'<actual0ea source-bound ordinary Root qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
