"""Same sealed a9 native joined only to successful corrected Test source and all Main bytes."""
import inspect
import pg2922_same_a9_native_rejoin as prior
from pg2930_format_fixed_db_full_six import validate


def qualify_snapshot():
    raw=inspect.getsource(prior.qualify_snapshot).replace('pg2920-db-failure-group-full-qualified-v1','pg2932-format-fixed-full-qualified-v1')
    ns={**prior.__dict__,'validate':validate}
    exec(compile(raw,'<actual corrected full input requirement>','exec'),ns);return ns['qualify_snapshot']()


def server():
    return prior.server().replace('PG2918','PG2930').replace('qualified2918Tests','qualified2930Tests').replace('PG2922','PG2934')


def source():
    return prior.source().replace('pg2922-same-a9-native-qualified-v1','pg2934-format-fixed-same-native-qualified-v1').replace('pg2920-db-failure-group-full-qualified-v1','pg2932-format-fixed-full-qualified-v1').replace('PG2922','PG2934')


def entry():
    ns={**prior.entry().__globals__,'CODE':server(),'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<actual corrected Test full same native rejoin>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
