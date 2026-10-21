"""Original4184 javap only; no new build, PT or actual native qualification."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6708_original4184_artifacts import read_whole

SQLSHA='8b7f9db189817cc953cdfaa94dc219336bf7424f86aa07faf284e0af9c749c42'


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (
      ('PG6672-current115-receivers-v1','PG6714-current115-receivers-v1'),
      ('pg6670-original4170-artifacts-v1','pg6708-original4184-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6718-sql58-original-jvm-v1'),
      ('pg6676_sql58_original_jvm.py','pg6718_sql58_original_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py' else 1
        if raw.count(before)!=count:raise ValueError('exact original JVM binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA}
    exec(compile(raw,'<original4184 JVM58>','exec'),scope)
    return scope['main']


if __name__=='__main__':definition()()
