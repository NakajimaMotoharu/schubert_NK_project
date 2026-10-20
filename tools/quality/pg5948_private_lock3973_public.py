"""Publish genuine current5944 XML once after independent qualification; no PT replay."""
import inspect
import pg5930_current3973_public as previous
from pg5946_private_lock_qualification import SOURCE, ROOT, W, SLOT as QUALIFIED, added_cases


def payload(data):
    raw = previous.payload(data).replace('PG5926', 'PG5944')
    if 'PG5926' in raw or 'Popen' in raw:
        raise ValueError('only original5944 artifact projection')
    compile(raw, '<original5944 case projection>', 'exec')
    return raw


def operator_source():
    raw = inspect.getsource(previous.main)
    for old, new in (('pg5930-current3973-projection-v1', 'pg5948-current3973-projection-v1'), ('PG5930-case-reader-v1', 'PG5948-case-reader-v1'),
                     ("public = base/'PG5926-current3973-cases'", "public = base/'PG5944-current3973-cases'"),
                     ('PG5886-current3973-cases', 'PG5926-current3973-cases'),
                     ('2045f1a9eb4eb60f2f470442bfbd3774f2925ce17cc88b5875d16f1163778d7f', '89bdeed7bf69067bb0a20c766c8e59cbb780d0fd83dffa7e71c9e1255b1115cf'),
                     ("allSeventeenTargetFour100=q['allSeventeenTargetFour100']", "privateLock34TargetFour100=q['privateLock34TargetFour100']")):
        if raw.count(old) != 1:
            raise ValueError('one original5944 projection namespace binding: '+old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<original5944 projection operator>', 'exec')
    return raw


def main():
    scope = {**vars(previous), 'SOURCE': SOURCE, 'ROOT': ROOT, 'W': W, 'QUALIFIED': QUALIFIED, 'added_cases': added_cases, 'payload': payload}
    exec(compile(operator_source(), '<original5944 projection>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
