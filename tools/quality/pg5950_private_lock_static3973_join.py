"""Join573 individual reasons to actual5944 original XML after independent qualification only."""
import pg5934_static3973_join as previous
from pg5944_private_lock_whole import SOURCE


def qualification_source():
    raw = previous.qualification_source()
    for old, new in (('PG5926-current3973-cases', 'PG5944-current3973-cases'),
                     ('pg5928-api-storage-qualified-v1', 'pg5946-private-lock-qualified-v1'),
                     ('pg5926-api-storage-six-v1', 'pg5944-private-lock-six-v1'),
                     ('pg5914-api-expression-static-v1', 'pg5942-private-lock-static-v1')):
        if raw.count(old) != 1:
            raise ValueError('one actual original5944 source/XML/class binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<current5944 original correspondences>', 'exec')
    return raw


def reader_source():
    raw = previous.reader_source()
    for old, new in (('(joined, static_only, len(result)) != (545, 239, 1544)', '(joined, static_only, len(result)) != (573, 239, 1451)'),
                     ('all545 reasons/all1544 warnings preserved,239 static-context-only premises', 'all573 reasons/all1451 warnings preserved,239 static-context-only premises'),
                     ('PG5934-current-static3973-v1', 'PG5950-current-static3973-v1'),
                     ('currentRawFindings=1544', 'currentRawFindings=1451')):
        if raw.count(old) != 1:
            raise ValueError('one current573 actual reason/XML join binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<current573 original XML joins>', 'exec')
    return raw


def main():
    scope = {**vars(previous.previous), 'SOURCE': SOURCE,
             'PENDING': previous.previous.BASE/'PG5960-readiness-boundaries28-v1/manifest.json',
             'PENDING_SHA': 'b24e154dde5b57f62f4a87081ea34ee001c89eb9e9b5226d63caa034a87912f3'}
    exec(compile(qualification_source(), '<original5944 qualified correspondence>', 'exec'), scope)
    exec(compile(reader_source(), '<all573 original5944 XML>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
