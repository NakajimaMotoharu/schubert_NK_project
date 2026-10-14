"""Read-only current cdbc image for candidate maintenance; no replay/retirement action."""
import ast
import inspect
import types
from pyflakes.api import check
import pg2410_retired_current_before as previous
import pg2476_question_current_backup_content as current

SLOT = 'pg2514-current-cdbc-before-v2'

CURRENT_FIELDS = {'backup', 'configuration', 'extraDurable', 'originals', 'pid1',
                  'rows', 'runtime', 'startup', 'unitFilesActual', 'units'}


def validate_current_image(after, native):
    if type(after) is not dict or set(after) != CURRENT_FIELDS or type(native) is not dict:
        raise ValueError('exact current ten original fields and separate native metadata required')
    return after


def payload(seals):
    # Reuse the proven schema extraction, but authenticate the current Source/run,
    # not the historical 3b retirement witness.
    raw = inspect.getsource(previous.payload)
    ns = {**previous.__dict__, 'prior': current}
    exec(compile(raw, '<current cdbc schema extraction factory>', 'exec'), ns)
    result = ns['payload'](seals).replace(previous.SLOT, SLOT)
    old = "require(set(after)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'})\nrequire(after['native']==native)\nflat={k:v for k,v in after.items()if k!='native'}"
    if result.count(old) != 1:
        raise ValueError('one historical schema extraction to replace required')
    result = result.replace(old, 'flat=validate_current_image(after,native)')
    result = 'CURRENT_FIELDS=' + repr(CURRENT_FIELDS) + '\n' + inspect.getsource(validate_current_image) + '\n' + result
    marker = "save=base/'" + SLOT + "'"
    if result.count(marker) != 1:
        raise ValueError('one new-only image extraction boundary required')
    guard = """require(data['source']['commit']=='cdbc07cdf77370d521e64de8b327da7f6752139b')
require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf'))
require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1980-once-resume.conf'))
"""
    result = result.replace(marker, guard + marker)
    if check('HASHES={}\nRECEIPT="actual"\n' + result, '<current cdbc read-only original image>'):
        raise ValueError('complete current extraction namespace required')
    ast.parse(result)
    return result


def entry():
    fn = current.entry()
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload}, 'current_cdbc_before')


if __name__ == '__main__':
    raise SystemExit(entry()())
