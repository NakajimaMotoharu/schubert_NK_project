"""Full new finite publication ABI; fixed qualified current shared class inputs only."""
import types
from pyflakes.api import check
from bundle_hash_contract import require_bound
import pg3996_literal_invariant_ro_compile as ro_compile
import pg4002_literal_invariant_publication_sources as role

TARGET = role.W / role.TOOLS


def generated():
    values = role.sources(); digest = ro_compile.sha(ro_compile.PRIOR / 'bundle.safe.json')
    values['pg4002_native_refs.py'] = 'BUNDLE_HASH=' + repr(digest) + '\n' + values['pg4002_native_refs.py']
    require_bound(values['pg4002_native_refs.py'], digest)
    for name, raw in values.items():
        if name.endswith('.py') and check(raw, '<new finite publication actual sources>'): raise ValueError('complete publication namespace required')
    return values


def compiler():
    raw = ro_compile.compiler().replace('pg3996-', 'pg4004-')
    raw = raw.replace("role.CLASS.replace('CandidateRo',suffix)", "'Pg4002'+suffix")
    marker = "('input','InputBoundaryTest')"
    if raw.count(marker) != 1: raise ValueError('all five shared tests plus finite transition test required')
    return raw.replace(marker, marker + ",('transition','TransitionTest')")


def main():
    namespace = {**ro_compile.previous.__dict__, 'role': role, 'TARGET': TARGET, 'PRIOR': ro_compile.PRIOR, 'generated': generated}
    namespace['write'] = types.FunctionType(ro_compile.previous.write.__code__, namespace)
    exec(compile(compiler(), '<full new finite publication ABI>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
