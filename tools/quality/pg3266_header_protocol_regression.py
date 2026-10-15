"""Related Protocol84 after Header oracle fix; Main/resource member identity, no VM."""
import inspect
from pyflakes.api import check
import pg2634_protocol_oracle_regression as old
from pg3258_statement_group_full_six import SOURCE


def server():
    raw = old.SERVER.replace('PG2634-v2', 'PG3266-v1').replace('PG2620', 'PG3248').replace('tests==82', 'tests==84')
    marker = "tests+=int(x.get('tests'))"
    if raw.count(marker) != 1:
        raise ValueError('one XML count boundary required')
    raw = raw.replace(marker, "cases=x.findall('testcase');require(len(cases)==int(x.get('tests')) and not any('rerun'in n.tag.lower()or'flaky'in n.tag.lower()for n in x.iter()));require(len({(c.get('classname'),c.get('name'))for c in cases})==len(cases));tests+=len(cases)")
    raw = raw.replace("inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()}",
                      "inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()};require((source/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/header/HeaderModelTest.java').read_text().count('@Test\\n')==7)")
    if check('INPUT={}\n' + raw, '<current Header Protocol84>'):
        raise ValueError('complete namespace required')
    compile(raw, '<independent Protocol84 real JUnit/static/counters>', 'exec')
    return raw


def main():
    raw = inspect.getsource(old.main).replace('PG2634-v2', 'PG3266-v1')
    raw = raw.replace('pg2621-permit-expiry-group-full-qualified-v1', 'pg3250-cycle-group-full-qualified-v1')
    ns = {**old.__dict__, 'SOURCE': SOURCE, 'SLOT': 'pg3266-header-protocol-regression-v1', 'SERVER': server()}
    exec(compile(raw, '<current Header regression transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
