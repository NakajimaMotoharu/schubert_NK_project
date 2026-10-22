"""Original4209 Jar/JVM SQL guard join only, no build/PT replay."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6864_original4209_artifacts import read_whole

SQLSHA='8533553c7fe58aef5841763b550f528764d209223ac97eebfeb10590727376c1'


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in(('PG6672-current115-receivers-v1','PG6866-current115-web-receivers-v1'),('pg6670-original4170-artifacts-v1','pg6864-original4209-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6870-sql58-current-jvm-v1'),('pg6676_sql58_original_jvm.py','pg6870_sql58_current_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py'else 1
        if raw.count(before)!=count:raise ValueError('one exact JVM path binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA};exec(compile(raw,'<current4209 JVM58>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
