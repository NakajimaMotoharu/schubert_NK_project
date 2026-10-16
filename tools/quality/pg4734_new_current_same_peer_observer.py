"""New normal-current immutable same-peer observer; never starts or stops business Units."""
from pathlib import Path
import pg4220_same_peer_current_observer as previous
import pg4722_ssc299_publication_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
from pg4434_current_candidate_admission_read import authenticate_host

SOURCE,BOM=role.SOURCE,role.BOM
PREFIX='pg4734'


def bind(raw):
    raw=role.ro.unused.normalized_text(raw)
    return (raw.replace('pg4220',PREFIX).replace('PG4220','PG4734')
            .replace('pg4008-literal-invariant-publication-independent-post-v1','pg4728-ssc299-publication-independent-post-v1'))


def files():
    original=previous.namespace()['files']()
    return {('pg4734_watch_parent.py'if name=='pg4220_watch_parent.py'else name):
            (bind(raw)if name=='pg4220_watch_parent.py'else raw)for name,raw in original.items()}


def source():return bind(previous.source())


def namespace():
    ns={'__file__':str(Path(__file__).parent/'vm/050_s1/pg4734_new_current_same_peer_observer.py'),
        '__name__':'ssc299_normal_current_samepeer','OBSERVER_FILES':files()}
    exec(compile(source(),'<new normal current immutable observer>','exec'),ns)
    return ns


def main():
    import sys
    authenticate_host()
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
