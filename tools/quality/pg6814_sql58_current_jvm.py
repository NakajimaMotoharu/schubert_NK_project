"""Original4202 Jar/JVM SQL guards only, no build/PT replay."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6804_original4202_artifacts import read_whole

SQLSHA='de1f8f41a413cef82ba5c4ce7a96015bfbbd3e7fe56292326eef496c918aaba9'


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (('PG6672-current115-receivers-v1','PG6810-current115-correlation-receivers-v1'),('pg6670-original4170-artifacts-v1','pg6804-original4202-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6814-sql58-current-jvm-v1'),('pg6676_sql58_original_jvm.py','pg6814_sql58_current_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py'else 1
        if raw.count(before)!=count:raise ValueError('exact JVM path binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA};exec(compile(raw,'<current4202 JVM58>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
