"""New04bb immutable same-peer observer; no business start or stop."""
from pathlib import Path
import pg4734_new_current_same_peer_observer as previous
import pg4880_ssc301_302_publication_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
from pg4434_current_candidate_admission_read import authenticate_host

SOURCE,BOM=role.SOURCE,role.BOM
PREFIX='pg4890'


def bind(raw):
    raw=role.ro.unused.normalized_text(raw)
    return raw.replace('pg4734',PREFIX).replace('PG4734','PG4890').replace('pg4728-ssc299-publication-independent-post-v1','pg4886-ssc301-302-publication-independent-post-v1')


def files():
    return {('pg4890_watch_parent.py' if name=='pg4734_watch_parent.py' else name):
            (bind(raw) if name=='pg4734_watch_parent.py' else raw) for name,raw in previous.files().items()}


def source():return bind(previous.source())


def namespace():
    ns={'__file__':str(Path(__file__).parent/'vm/050_s1/pg4890_new_current_same_peer_observer.py'),
        '__name__':'ssc301302_current_samepeer','OBSERVER_FILES':files()}
    exec(compile(source(),'<new04bb immutable observer>','exec'),ns);return ns


def main():
    import sys
    authenticate_host()
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
