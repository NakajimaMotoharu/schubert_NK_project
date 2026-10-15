"""Existing sealed28, new3699 and every1643/79 member, no VM action or recopy."""
import inspect
import pg3252_cycle_group_native_rejoin as previous
from pg3258_statement_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def build(*args):
    raw = inspect.getsource(previous.build).replace('3697', '3699').replace('PG3248', 'PG3258').replace('PG3252', 'PG3262')
    ns = dict(previous.__dict__)
    exec(compile(raw, '<sealed native28 new3699 builder>', 'exec'), ns)
    return ns['build'](*args)


def main():
    raw = inspect.getsource(previous.main).replace('pg3250-cycle-group-full-qualified-v1', 'pg3260-statement-group-full-qualified-v1')
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'build': build, 'OUT': W / 'pg3262-statement-group-native-qualified-v1'}
    exec(compile(raw, '<new3699 native28 read-only transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
