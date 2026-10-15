"""Requalify sealed28 against whole3702 all Main/resource/debug bytes. No VM."""
import inspect
from pyflakes.api import check

import pg3278_header_group_native_rejoin as previous
from pg3302_directional_group_full_six import SOURCE, validate
from pg3274_header_group_full_six import rebase


def build(*args):
    raw = rebase(inspect.getsource(previous.build), 'PG3274', 'PG3302', 3701, 3702).replace('PG3278', 'PG3306')
    namespace = dict(previous.__dict__)
    exec(compile(raw, '<native28 and directional3702 fixed provenance>', 'exec'), namespace)
    result = namespace['build'](*args)
    if check(result, '<native28 directional3702 complete namespace>'):
        raise ValueError('complete native qualifier namespace required')
    return result


def public_summary(value):
    raw = rebase(inspect.getsource(previous.public_summary), 'PG3274', 'PG3302', 3701, 3702)
    namespace = {**previous.__dict__, 'SOURCE': SOURCE}
    exec(compile(raw, '<actual whole3702/native28 summary>', 'exec'), namespace)
    return namespace['public_summary'](value)


def main():
    raw = inspect.getsource(previous.main).replace('pg3276-header-group-full-qualified-v1', 'pg3304-directional-group-full-qualified-v1').replace('pg3278-header-group-native-qualified-v1', 'pg3306-directional-group-native-qualified-v1')
    namespace = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'build': build, 'public_summary': public_summary}
    exec(compile(raw, '<sealed28 and new3702 requalification>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
