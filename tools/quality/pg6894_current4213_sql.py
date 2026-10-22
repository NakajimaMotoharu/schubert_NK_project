"""Same-source4213 original SQL115, no new PT or runtime action."""
import inspect
import pg6672_current115_receivers as prior
from pg6892_original4213_artifacts import read_whole


def definition():
    raw = inspect.getsource(prior.main)
    if raw.count('PG6672-current115-receivers-v1') != 1 or raw.count('currentWholeTests=4170') != 1:
        raise ValueError('one exact output and count')
    raw = raw.replace('PG6672-current115-receivers-v1', 'PG6894-current4213-sql-v1').replace('currentWholeTests=4170', 'currentWholeTests=4213')
    scope = {**vars(prior), 'read_whole': read_whole}
    exec(compile(raw, '<current4213 SQL115>', 'exec'), scope)
    return scope['main']


if __name__ == '__main__':
    definition()()
