"""Necessary whole integration of the seventh failed-pair test, same a9 Main."""
import inspect
import pg2930_format_fixed_db_full_six as previous
from pyflakes.api import check

SOURCE = previous.SOURCE


def validate(snapshot):
    raw = inspect.getsource(previous.prior.validate)
    raw = raw.replace('pg2912-jdbc-compound-close-selected-v2', 'pg2926-jdbc-format-selected-v1').replace('pg2916-failed-pair-boundary-selected-v1', 'pg2938-extra-row-selected-v1')
    old = "'pg2938-extra-row-selected-v1',FAILURE,6"
    if raw.count(old) != 1:
        raise ValueError('one actual seven-test input boundary required')
    raw = raw.replace(old, "'pg2938-extra-row-selected-v1',FAILURE,7")
    ns = dict(previous.prior.__dict__)
    exec(compile(raw, '<exact actual Session61 failedPair7 inputs>', 'exec'), ns)
    return ns['validate'](snapshot)


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2930', 'PG3026').replace('3684', '3685')
    if check(raw, '<whole3685 all-six-format-first>'):
        raise ValueError('complete current server namespace required')
    compile(raw, '<whole3685 same a9 Main>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.prior.main).replace('PG2918', 'PG3026').replace('pg2918', 'pg3026').replace('3684', '3685')
    raw = raw.replace('3680 retained plus one compound Session close and three failed-pair identity/null methods; Main unchanged;542suite1643', '3684 retained plus one independently selected extra-row failed-pair method; Main unchanged;542suite1643')
    raw = raw.replace('Four independently real-DB methods require one fresh Test-input integration; same a9 Main must independently match actual PG2802 and its native9; no Root/VM replay', 'One independently selected extra-row method requires new3685 integration; same a9 Main must match PG2802 and qualified native; no Root/VM replay')
    ns = {**previous.prior.__dict__, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<new seven failedPair integration full campaign>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
