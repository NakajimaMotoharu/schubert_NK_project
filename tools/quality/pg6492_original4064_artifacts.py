"""Collect genuine original4064 once; no old PASS arithmetic or regression replay."""
import inspect
import pg6198_original4024_artifacts as prior
from pg6496_web_owned_component_qualification_v4 import original_source

OLD = 'bbbc3f7f13b6858535515dc495ad53839683fb24'


def definitions():
    scope = {**vars(prior), 'OLD': OLD, 'original_source': original_source}
    for name in ('new_case_identities', 'main'):
        raw = inspect.getsource(getattr(prior, name))
        for before, after in (
            ('!=36', '!=8'), ('exact36', 'exact8'), ('len(owners)!=13', 'len(owners)!=1'), ('exact13', 'exact1'),
            ('pg6196-management-ownership-six-v1', 'pg6490-web-component-six-v1'), ('PG6196-six-v1', 'PG6490-six-v1'), ('PG6196', 'PG6490'),
            ('PG6118-current3988-cases', 'PG6452-current4056-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23', 'bddf967441ed173d5a9e89287c0d3b9916b9afcc07d15510d4f38878b63c5124'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47', '7a9845f00f2acd70fb569909365753dac2f91b01e52d32cd580943ac649565b8'),
            ('PG6193-management-primary-qualification-v2', 'PG6496-web-owned-component-qualification-v4'),
            ('pg6193-management-primary-qualification-v2', 'pg6496-web-owned-component-qualification-v4'),
            ('(60,20)', '(27,11)'), ('source60', 'source27'), ('[4024,605,1667]', '[4064,612,1667]'),
            ('pg6198-original4024-artifacts-v1', 'pg6492-original4064-artifacts-v1'),
            ('PG6198-original4024-v1', 'PG6492-original4064-v1'), ('PG6490-current4024-cases', 'PG6490-current4064-cases')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<original4064 '+name+'>', 'exec'), scope)
    return scope


def new_case_identities(source): return definitions()['new_case_identities'](source)
def main(): return definitions()['main']()


if __name__ == '__main__':
    main()
