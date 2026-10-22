"""Current4197 original Jar/JVM SQL guards only, no additional build/PT."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6786_original4197_web_artifacts import read_whole

SQLSHA='cf14b128e28d6cddf3bc2a96ce0b266122e5c3ecd45a4d89dae43dafa25de54d'


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (('PG6672-current115-receivers-v1','PG6788-current115-web-receivers-v1'),('pg6670-original4170-artifacts-v1','pg6786-original4197-web-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6792-sql58-web-jvm-v1'),('pg6676_sql58_original_jvm.py','pg6792_sql58_web_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py'else 1
        if raw.count(before)!=count:raise ValueError('exact JVM path binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA};exec(compile(raw,'<Web4197 JVM58>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
