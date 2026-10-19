"""Fresh0ea four-file same-peer observer; old signed identities are not authority."""
from pathlib import Path
import re
import pg5466_new_current_same_peer_observer as previous
import pg5624_current_publication_sources as role
from immutable_payload_binding import bind_preserving_payloads
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
from pg4996_resume_connection import authenticate_host

SOURCE,BOM=role.SOURCE,role.BOM
PREFIX='pg5634'


def bind(raw):
    changes={previous.SOURCE:SOURCE,previous.BOM:BOM,'pg5466':PREFIX,'PG5466':'PG5634',
      'pg5460-ownership-publication-independent-post-v1':'pg5630-current-publication-independent-post-v1',
      'PG5430':'PG5598','pg5430-manifest.sig':'pg5598-manifest.sig'}
    pattern='|'.join(re.escape(k)for k in sorted(changes,key=len,reverse=True))
    return bind_preserving_payloads(raw,lambda text:re.sub(pattern,lambda match:changes[match.group()],text))


def files():
    return{('pg5634_watch_parent.py'if name=='pg5466_watch_parent.py'else name):
      (bind(raw)if name=='pg5466_watch_parent.py'else raw)for name,raw in previous.files().items()}


def source():return bind(previous.source())


def namespace():
    ns={'__file__':str(Path(__file__).parent/'vm/050_s1/pg5634_new_current_same_peer_observer.py'),
      '__name__':'current0ea_samepeer','OBSERVER_FILES':files()}
    exec(compile(source(),'<new0ea immutable samepeer observer>','exec'),ns)
    return ns


def main():
    import sys
    authenticate_host()
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':main()
