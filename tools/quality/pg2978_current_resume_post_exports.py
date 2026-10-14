"""BUG1261 new-only post: actual same export and sealed declaration parser ABI."""
import types
import pg2976_current_resume_independent_post as previous

SLOT = 'pg2978-current-resume-independent-post-v1'
EXPORTS = r'''
from pg2970_configuration import same as config_same
parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
node=next(n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
parser_scope={'re':re}
exec(compile(ast.Module(body=[node],type_ignores=[]),'<sealed independent declaration parser>', 'exec'),parser_scope)
exec_record=parser_scope['exec_record']
'''


def payload(seals):
    raw = previous.payload(seals).replace(previous.SLOT, SLOT).replace('PG2976', 'PG2978')
    old = 'from pg2970_configuration import exec_record,config_same'
    if raw.count(old) != 1:
        raise ValueError('one failed export binding required')
    raw = raw.replace(old, EXPORTS)
    old = "'independentResumeOnlyDeltaVerified':True"
    if raw.count(old) != 1:
        raise ValueError('one bounded proof result required')
    raw = raw.replace(old, old + ",'preparedAfterSha256':hashlib.sha256(fresh_private('after.private.json')).hexdigest(),'nativeCanonicalSha256':hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest()")
    compile(raw, '<corrected independent post exports>', 'exec')
    return raw


def entry():
    fn = previous.entry()
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload}, 'corrected_exports_independent_post')


if __name__ == '__main__':
    raise SystemExit(entry()())
