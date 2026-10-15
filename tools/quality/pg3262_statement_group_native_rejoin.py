"""Existing sealed28, new3699 and every1643/79 member, no VM action or recopy."""
import inspect
import pg3252_cycle_group_native_rejoin as previous
from pg3258_statement_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def public_summary(value):
    result = value['result']
    expected = {'actualExit': 0, 'qualifiedFullTests': 3699, 'qualifiedNativeStreams': 28,
                'distinctSessions': 28, 'mainClassesIdentical': 1643,
                'allResourceMetaMembersIdentical': 79, 'productionSource': SOURCE}
    if value['actualExit'] != 0 or any(result[k] != v for k, v in expected.items()):
        raise ValueError('actual new3699/native28 result required for public summary')
    return {'tests': result['qualifiedFullTests'], 'streams': result['qualifiedNativeStreams'],
            'mainClassesSameBytes': result['mainClassesIdentical'],
            'resourceMetaSameBytes': result['allResourceMetaMembersIdentical'],
            'classByteMismatch': 0,
            'remaining': {k: sum(v[k]['missed'] for v in result['moduleCounters'].values())
                          for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']},
            'manifestSha256': value['manifestSha256']}


def build(*args):
    raw = inspect.getsource(previous.build).replace('3697', '3699').replace('PG3248', 'PG3258').replace('PG3252', 'PG3262')
    ns = dict(previous.__dict__)
    exec(compile(raw, '<sealed native28 new3699 builder>', 'exec'), ns)
    return ns['build'](*args)


def main_source():
    raw = inspect.getsource(previous.main).replace('pg3250-cycle-group-full-qualified-v1', 'pg3260-statement-group-full-qualified-v1')
    lines = [line for line in raw.splitlines() if 'safe.update(tests=3697,' in line]
    if len(lines) != 1:
        raise ValueError('one old literal summary boundary required')
    line = lines[0]
    return raw.replace(line, line[:line.index('safe.update(')] + 'safe.update(public_summary(value))')


def main():
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'build': build,
          'public_summary': public_summary, 'OUT': W / 'pg3262-statement-group-native-qualified-v1'}
    exec(compile(main_source(), '<new3699 native28 read-only transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
