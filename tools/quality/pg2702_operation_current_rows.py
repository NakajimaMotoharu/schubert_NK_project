"""Independent all24 DB postconditions from actual new admission original."""
import inspect
import pg2546_strict_current_rows as previous
from pg2698_operation_admission_before import before
from pg2674_operation_publication_sources import production

SOURCE=production();SLOT='pg2702-operation-current-rows-v1'


def payload():
    raw=inspect.getsource(previous.payload).replace('pg2542-strict-current-live-binding-v1','pg2686-operation-current-live-binding-v1').replace('pg2540-strict-current-noargs-once-v1','pg2684-operation-current-noargs-once-v1')
    ns={**previous.__dict__,'BEFORE':before(),'SLOT':SLOT,'SOURCE':SOURCE}
    exec(compile(raw,'<actual new admission DB factory>','exec'),ns);return ns['payload']()


def entry():
    raw=inspect.getsource(previous.entry).replace('pg2544-strict-current-terminal-v1','pg2700-operation-current-terminal-v1')
    ns={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new all24 independent transport>','exec'),ns);return ns['entry']()


if __name__=='__main__':raise SystemExit(entry()())
