"""Original Test-only whole collector; strict empty Main delta, no historical profile edits."""
import inspect
from types import SimpleNamespace
import pg6042_original3976_artifacts as reader
import pg6198_original4024_artifacts as prior
from pg6524_finite_defaults_whole import original_source

OLD = 'e45cfd31c8d610922f4e9432cc1cf11fa9b48338'


def emitted(data_hash, remote):
    raw = reader.emitted(data_hash, remote)
    anchor = "('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor) != 1 or raw.count("'PG6490')") != 1:
        raise ValueError('one new isolated whole profile and one coverage export guard')
    raw = raw.replace(anchor, "('PG6490', (4064, 612, 1667), 1), ('PG6524', (4073, 614, 1667), 0))", 1)
    raw = raw.replace("'PG6490')", "'PG6490', 'PG6524')", 1)
    anchor = '    added = set(after)-set(before); removed = set(before)-set(after)'
    if raw.count(anchor) != 1:
        raise ValueError('one strict physical comparison implementation')
    pure = ("    if not owners:\n"
            "        if tuple(expected_counts) != (1667, 1667) or expected_added != [] or len(before) != 1667 or before != after:\n"
            "            raise ValueError('Test-only whole requires all1667 exactly identical; no Main change accepted')\n"
            "        return [], [], 1667\n")
    raw = raw.replace(anchor, pure+anchor, 1)
    compile(raw, '<isolated original4073 reader>', 'exec')
    return raw


def collect(*args, **kwargs):
    raw = inspect.getsource(reader.collect)
    if raw.count("'PG6490')") != 1:
        raise ValueError('one explicit original coverage import guard')
    scope = {**vars(reader), 'emitted': emitted}
    exec(compile(raw.replace("'PG6490')", "'PG6490', 'PG6524')", 1), '<isolated4073 collect>', 'exec'), scope)
    return scope['collect'](*args, **kwargs)


def definitions():
    scope = {**vars(prior), 'OLD': OLD, 'original_source': original_source,
             'reader': SimpleNamespace(**{**vars(reader), 'collect': collect})}
    for name in ('new_case_identities', 'main'):
        raw = inspect.getsource(getattr(prior, name))
        for before, after in (
            ('!=36', '!=9'), ('exact36', 'exact9'), ('len(owners)!=13', 'len(owners)!=0'), ('exact13', 'exact0'),
            ('pg6196-management-ownership-six-v1', 'pg6524-finite-defaults-six-v1'),
            ('PG6196-six-v1', 'PG6524-six-v1'), ('PG6196', 'PG6524'),
            ('PG6118-current3988-cases', 'PG6490-current4064-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23', 'c226dd9d40c491c44edf7a598aa9748ca90a58229b8849b8a6936cea136fb811'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47', '6078b18c20f40b16cff87155187228c16e607a923a455e42d4d2e9e481462862'),
            ('PG6193-management-primary-qualification-v2', 'PG6522-maintenance-owner-qualification-v1'),
            ('pg6193-management-primary-qualification-v2', 'pg6522-maintenance-owner-qualification-v1'),
            ('(60,20)', '(15,8)'), ('source60', 'source15'),
            ('[4024,605,1667]', '[4073,614,1667]'),
            ('pg6198-original4024-artifacts-v1', 'pg6526-original4073-artifacts-v1'),
            ('PG6198-original4024-v1', 'PG6526-original4073-v1'),
            ('PG6524-current4024-cases', 'PG6524-current4073-cases')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<original4073 '+name+'>', 'exec'), scope)
    return scope


def new_case_identities(source): return definitions()['new_case_identities'](source)
def main(): return definitions()['main']()


if __name__ == '__main__':
    main()
