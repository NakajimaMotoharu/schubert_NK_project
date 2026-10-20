"""Join545 current reasons only to genuine current3973 XML; never execute tests or runtime."""
import inspect
import pg5902_static3973_join as previous
from pg5926_api_storage_whole import SOURCE


def qualification_source():
    raw = inspect.getsource(previous.qualified_whole)
    for old, new in (('PG5886-current3973-cases', 'PG5926-current3973-cases'),
                     ('pg5888-terminal-serial-qualified-v1', 'pg5928-api-storage-qualified-v1'),
                     ('pg5886-terminal-serial-six-v1', 'pg5926-api-storage-six-v1'),
                     ('pg5882-terminal-serial-static-v1', 'pg5914-api-expression-static-v1')):
        if raw.count(old) != 1:
            raise ValueError('one current original3973 source/XML/class binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<current3973 original artifact correspondence>', 'exec')
    return raw


def reader_source():
    raw = inspect.getsource(previous.main)
    changes = {'(joined, static_only, len(result)) != (528, 239, 1586)': '(joined, static_only, len(result)) != (545, 239, 1544)',
               'all528 reasons/all1586 warnings preserved,239 static-context-only premises': 'all545 reasons/all1544 warnings preserved,239 static-context-only premises',
               'PG5902-current-static3973-v1': 'PG5934-current-static3973-v1',
               'currentRawFindings=1586': 'currentRawFindings=1544'}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one exact current545 reason binding: ' + old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<current545 original XML join>', 'exec')
    return raw


def main():
    scope = {**vars(previous), 'SOURCE': SOURCE,
             'PENDING': previous.BASE/'PG5924-direct-boundary13-v1/manifest.json',
             'PENDING_SHA': '93cf3ddad9386c7e1a670b0d8d2aae836fba454f7be1ae534de674e81a4a4b65'}
    exec(compile(qualification_source(), '<current3973 correspondence>', 'exec'), scope)
    exec(compile(reader_source(), '<current545 original XML join>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
