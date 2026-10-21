"""Collect original4056 once; no old PASS arithmetic or whole replay."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6450_morning_sequence_qualification import original_source

OLD = '669ad5fd83f67ad031b2c1734d7fc5716599d35d'


def definitions():
    scope = {**vars(prior), 'OLD': OLD, 'original_source': original_source}
    for name in ('new_case_identities', 'main'):
        raw = inspect.getsource(getattr(prior, name))
        for before, after in (
            ('!=36', '!=2'), ('exact36', 'exact2'), ('len(owners)!=13', 'len(owners)!=1'), ('exact13', 'exact1'),
            ('pg6196-management-ownership-six-v1', 'pg6452-morning-completion-six-v1'), ('PG6196-six-v1', 'PG6452-six-v1'), ('PG6196', 'PG6452'),
            ('PG6118-current3988-cases', 'PG6408-current4054-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23', '2fe8efc5bc8ad1c60487a1366ba80c159fe8c61cf937fd2509b8d4298591b0a7'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47', '60e3e6b6b8ab01b0cedfeb557518012b168a852b67550dd39c92fbc5103cd886'),
            ('PG6193-management-primary-qualification-v2', 'PG6450-morning-sequence-qualification-v1'),
            ('pg6193-management-primary-qualification-v2', 'pg6450-morning-sequence-qualification-v1'),
            ('(60,20)', '(23,10)'), ('source60', 'source23'), ('[4024,605,1667]', '[4056,610,1667]'),
            ('pg6198-original4024-artifacts-v1', 'pg6454-original4056-artifacts-v1'),
            ('PG6198-original4024-v1', 'PG6454-original4056-v1'), ('PG6452-current4024-cases', 'PG6452-current4056-cases')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<original4056 '+name+'>', 'exec'), scope)
    return scope


def new_case_identities(source): return definitions()['new_case_identities'](source)
def main(): return definitions()['main']()


if __name__ == '__main__':
    main()
