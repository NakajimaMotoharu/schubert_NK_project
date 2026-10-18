"""Fresh immutable a2ecc observer, four fixed files/single peer; never starts Units."""
from pathlib import Path
import pg4890_new_current_same_peer_observer as previous
import pg5008_ssc304_publication_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
from pg4996_resume_connection import authenticate_host

SOURCE, BOM = role.SOURCE, role.BOM
PREFIX = 'pg5018'


def bind(raw):
    raw = role.ro.unused.normalized_text(raw)
    return (raw.replace('pg4890', PREFIX).replace('PG4890', 'PG5018')
            .replace('pg4886-ssc301-302-publication-independent-post-v1', 'pg5014-ssc304-publication-independent-post-v1'))


def files():
    return {('pg5018_watch_parent.py' if name == 'pg4890_watch_parent.py' else name):
            (bind(raw) if name == 'pg4890_watch_parent.py' else raw)
            for name, raw in previous.files().items()}


def source():
    return bind(previous.source())


def namespace():
    ns = {'__file__': str(Path(__file__).parent / 'vm/050_s1/pg5018_new_current_same_peer_observer.py'),
          '__name__': 'ssc304_current_samepeer', 'OBSERVER_FILES': files()}
    exec(compile(source(), '<newa2ecc immutable observer>', 'exec'), ns)
    return ns


def main():
    import sys
    authenticate_host()
    if sys.argv[1:] == ['stage']:
        with management_gate(P / 'current-management-critical.lock'):
            return namespace()['main']()
    return namespace()['main']()


if __name__ == '__main__':
    main()
