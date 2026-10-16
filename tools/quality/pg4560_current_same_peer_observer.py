"""New immutable observer for published964e; no start/stop or old session reuse."""
from pathlib import Path
import pg4220_same_peer_current_observer as previous
import pg4540_failed_current_publication_sources as role
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P

SOURCE,BOM=role.SOURCE,role.BOM
PREFIX='pg4560'


def bind(raw):
    raw=role.ro.unused.previous.previous.role_text(raw)
    return raw.replace('pg4220',PREFIX).replace('PG4220','PG4560').replace('pg4008-literal-invariant-publication-independent-post-v1','pg4552-failed-current-publication-post-v1')


def files():
    values=previous.namespace()['files']()
    return {('pg4560_watch_parent.py'if name=='pg4220_watch_parent.py'else name):(bind(raw)if name=='pg4220_watch_parent.py'else raw)for name,raw in values.items()}


def source():
    return bind(previous.source())


def namespace():
    values={'__file__':str(Path(__file__).parent/'vm/050_s1/pg4560_current_same_peer_observer.py'),'__name__':'new964e_same_peer_observer','OBSERVER_FILES':files()}
    exec(compile(source(),'<new published964e immutable observer>','exec'),values);return values


def main():
    import sys
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
