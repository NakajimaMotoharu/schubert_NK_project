"""Original4189 javap only; no rebuild/PT/native qualification."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6750_original4189_owned_artifacts import read_whole

SQLSHA=None


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (('PG6672-current115-receivers-v1','PG6752-current115-owned-receivers-v1'),
      ('pg6670-original4170-artifacts-v1','pg6750-original4189-owned-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6756-sql58-owned-jvm-v1'),
      ('pg6676_sql58_original_jvm.py','pg6756_sql58_owned_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py' else 1
        if raw.count(before)!=count:raise ValueError('exact original JVM binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA}
    exec(compile(raw,'<owned4189 JVM58>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
