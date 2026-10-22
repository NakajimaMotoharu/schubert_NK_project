"""Actual original4213 Jar disassembly, SQL58 only; no PT/native replay."""
import inspect
import pg6676_sql58_original_jvm as prior
from pg6892_original4213_artifacts import read_whole

SQLSHA = '8236b7197818d381830ddc29c0a60a461ca57cb79dfe694515898eebe554a27e'


def definition():
    raw = inspect.getsource(prior.main)
    for before, after in (('PG6672-current115-receivers-v1', 'PG6894-current4213-sql-v1'),
        ('pg6670-original4170-artifacts-v1', 'pg6892-original4213-artifacts-v1'),
        ('PG6676-sql58-original-jvm-v1', 'PG6898-current4213-jvm-v1'),
        ('pg6676_sql58_original_jvm.py', 'pg6898_current4213_jvm.py')):
        count = 2 if before == 'pg6676_sql58_original_jvm.py' else 1
        if raw.count(before) != count:
            raise ValueError('exact JVM path binding ' + before)
        raw = raw.replace(before, after, count)
    scope = {**vars(prior), 'read_whole': read_whole, 'SQLSHA': SQLSHA}
    exec(compile(raw, '<original4213 JVM58>', 'exec'), scope)
    return scope['main']


if __name__ == '__main__':
    definition()()
