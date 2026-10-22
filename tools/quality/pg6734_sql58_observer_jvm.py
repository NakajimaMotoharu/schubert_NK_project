"""Observer4184 original javap only; no PT, rebuild or native campaign."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6728_original4184_observer_artifacts import read_whole

SQLSHA=None


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (
      ('PG6672-current115-receivers-v1','PG6730-current115-observer-receivers-v1'),
      ('pg6670-original4170-artifacts-v1','pg6728-original4184-observer-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6734-sql58-observer-jvm-v1'),
      ('pg6676_sql58_original_jvm.py','pg6734_sql58_observer_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py' else 1
        if raw.count(before)!=count:raise ValueError('exact original JVM binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA}
    exec(compile(raw,'<observer4184 JVM58>','exec'),scope)
    return scope['main']


if __name__=='__main__':definition()()
