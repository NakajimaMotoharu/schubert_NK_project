"""Qualify only genuine original4052 artifacts; do not replay a missing/unreturned run."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6384_web_fatal_callback_retry_qualification import original_source

OLD = 'aed19c6dca368e9717309d6f744d7917c6b7b32c'


def definitions():
    scope = {**vars(prior), 'OLD': OLD, 'original_source': original_source}
    for name in ('new_case_identities', 'main'):
        raw = inspect.getsource(getattr(prior, name))
        for before, after in (
            ('!=36', '!=4'), ('exact36', 'exact4'), ('len(owners)!=13', 'len(owners)!=2'), ('exact13', 'exact2'),
            ('pg6196-management-ownership-six-v1', 'pg6386-web-startup-six-v1'), ('PG6196-six-v1', 'PG6386-six-v1'), ('PG6196', 'PG6386'),
            ('PG6118-current3988-cases', 'PG6330-current4048-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23', '2b57d476af5f0d0e29c9b706220ba2f0c54ac8d2c4c22aac0685f45da14598d3'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47', 'd3a6e58f453e25c360cc9138ae733dab3a30aa0d2f9bec505f21ec66700fc4ce'),
            ('PG6193-management-primary-qualification-v2', 'PG6384-web-fatal-callback-retry-qualification-v1'),
            ('pg6193-management-primary-qualification-v2', 'pg6384-web-fatal-callback-retry-qualification-v1'),
            ('(60,20)', '(22,8)'), ('source60', 'source22'), ('[4024,605,1667]', '[4052,608,1667]'),
            ('pg6198-original4024-artifacts-v1', 'pg6388-original4052-artifacts-v1'),
            ('PG6198-original4024-v1', 'PG6388-original4052-v1'), ('PG6386-current4024-cases', 'PG6386-current4052-cases')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<original4052 '+name+'>', 'exec'), scope)
    return scope


def new_case_identities(source): return definitions()['new_case_identities'](source)
def main(): return definitions()['main']()


if __name__ == '__main__':
    main()
