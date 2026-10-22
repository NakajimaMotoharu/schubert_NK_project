"""Current original4222 SQL115 identities only; no PT/runtime replay."""
import inspect
import pg6894_current4213_sql as previous
from pg6932_original4222_artifacts import read_whole


def definition():
    raw = inspect.getsource(previous.definition)
    raw = raw.replace('PG6894-current4213-sql-v1', 'PG6934-current4222-sql-v1').replace('currentWholeTests=4213', 'currentWholeTests=4222')
    scope = {**vars(previous), 'read_whole': read_whole}
    exec(compile(raw, '<current4222 SQL115 definition>', 'exec'), scope)
    return scope['definition']()


if __name__ == '__main__':
    definition()()
