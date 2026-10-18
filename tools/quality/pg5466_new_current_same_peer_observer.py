"""Fresh296 four-file same-peer observer, no business start/stop or transferred authority."""
from pathlib import Path
import pg5018_new_current_same_peer_observer as previous
import pg5454_ownership_publication_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
from pg4996_resume_connection import authenticate_host

SOURCE,BOM=role.SOURCE,role.BOM
PREFIX='pg5466'


def bind(raw):
    raw=role.ro.unused.normalized_text(raw)
    return(raw.replace('pg5018',PREFIX).replace('PG5018','PG5466')
        .replace('pg5014-ssc304-publication-independent-post-v1','pg5460-ownership-publication-independent-post-v1'))


def files():
    return{('pg5466_watch_parent.py'if name=='pg5018_watch_parent.py'else name):
        (bind(raw)if name=='pg5018_watch_parent.py'else raw)for name,raw in previous.files().items()}


def source():return bind(previous.source())


def namespace():
    ns={'__file__':str(Path(__file__).parent/'vm/050_s1/pg5466_new_current_same_peer_observer.py'),
        '__name__':'ownership296_samepeer','OBSERVER_FILES':files()}
    exec(compile(source(),'<new296 immutable samepeer observer>','exec'),ns)
    return ns


def main():
    import sys
    authenticate_host()
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':main()
