"""Original4203 Jar/JVM SQL guard join only; no build/PT replay."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6830_original4203_artifacts import read_whole

SQLSHA=None


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (('PG6672-current115-receivers-v1','PG6832-current115-api-receivers-v1'),('pg6670-original4170-artifacts-v1','pg6830-original4203-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6836-sql58-current-jvm-v1'),('pg6676_sql58_original_jvm.py','pg6836_sql58_current_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py'else 1
        if raw.count(before)!=count:raise ValueError('exact JVM path binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA};exec(compile(raw,'<current4203 JVM58>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
