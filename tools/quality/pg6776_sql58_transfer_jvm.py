"""Original4197 javap SQL guards only; no new build or PT."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6770_original4197_transfer_artifacts import read_whole

SQLSHA=None


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (('PG6672-current115-receivers-v1','PG6772-current115-transfer-receivers-v1'),
      ('pg6670-original4170-artifacts-v1','pg6770-original4197-transfer-artifacts-v1'),
      ('PG6676-sql58-original-jvm-v1','PG6776-sql58-transfer-jvm-v1'),
      ('pg6676_sql58_original_jvm.py','pg6776_sql58_transfer_jvm.py')):
        count=2 if before=='pg6676_sql58_original_jvm.py'else 1
        if raw.count(before)!=count:raise ValueError('exact JVM path binding '+before)
        raw=raw.replace(before,after,count)
    scope={**vars(prior),'read_whole':read_whole,'SQLSHA':SQLSHA};exec(compile(raw,'<Transfer4197 JVM58>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
