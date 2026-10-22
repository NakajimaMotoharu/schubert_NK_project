"""Disassemble only returned original4222 jars for SQL58; no test/build replay."""
import inspect
import pg6898_current4213_jvm as previous
from pg6932_original4222_artifacts import read_whole

SQLSHA = 'dc52f79d5947261751e8594c23f1c48c07797b2fa50f99f5ee9373579a0761c1'


def definition():
    raw = inspect.getsource(previous.definition)
    for before, after in (('PG6894-current4213-sql-v1', 'PG6934-current4222-sql-v1'),
      ('pg6892-original4213-artifacts-v1', 'pg6932-original4222-artifacts-v1'),
      ('PG6898-current4213-jvm-v1', 'PG6938-current4222-jvm-v1'),
      ('pg6898_current4213_jvm.py', 'pg6938_current4222_jvm.py')):
        raw = raw.replace(before, after)
    scope = {**vars(previous), 'SQLSHA': SQLSHA, 'read_whole': read_whole}
    exec(compile(raw, '<current4222 original JVM definition>', 'exec'), scope)
    return scope['definition']()


if __name__ == '__main__':
    definition()()
