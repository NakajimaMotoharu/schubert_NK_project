"""New all11 before snapshot; no legacy missing-native projection or old10 copy."""
import inspect
import json
from pyflakes.api import check
import pg3000_current_resume_full_seal as previous
from pg1446_current_cold_stage import W
from pg2025_fresh_resume_full_live_seal import constant
from pg3130_browser_resume_terminal import payload as terminal_payload, SLOT as TERM

SLOT = 'pg3134-browser-resume-full-seal-v1'

NATIVE = r'''
require(type(before)is dict and set(before)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native'})
require(hashlib.sha256(json.dumps(before['native'],sort_keys=True).encode()).hexdigest()=='ab3fcad3e4f842562c7cd4cd77c5966b81ffba6534cf153c549cc1a5588aa4e2')
copied=BASE/'pg3122-prepared-browser-resume-once-v1/native-before-private'
manifest_copy=json.loads((copied.parent/'native-before-manifest.private.json').read_bytes())
expected_copy={str(pathlib.Path(k).relative_to('/run/schubert-nk/pt-coverage')):{'sha256':v['sha256'],'bytes':v['metadata'][6]}for k,v in before['native'].items()if k.endswith('.exec')}
require(manifest_copy==expected_copy and len(manifest_copy)==16)
for name,value in manifest_copy.items():
 p=copied/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p)and s.st_size==value['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256'])
require(before_shape(before))
'''


def rebind(raw, binding, started):
    raw = constant(raw, 'GUARD', 'NEW_TERMINAL_GUARD')
    raw = constant(raw, 'ORACLE', 'NEW_ALL24_ORACLE')
    old_once = json.loads((W / 'pg2984-current-fresh-resume-once-v1/manifest.safe.json').read_bytes())
    for old, new in [(previous.SLOT, SLOT), ('pg2984-current-fresh-resume-once-v1', 'pg3122-prepared-browser-resume-once-v1'), ('d10735e678e5053c0c96c55a42f65f2302132cfae902edd81dffbc2275c4c4ac', 'f041e0b3318db88e7b94cd40a23d28ba7e630d405e1b13f9ae397f03a1312f24')]:
        raw = raw.replace(old, new)
    begin = "require(type(before)is dict and set(before)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'})"
    start = raw.index(begin)
    end = raw.index('before=native_before_anchor(before);require(before_shape(before))', start) + len('before=native_before_anchor(before);require(before_shape(before))')
    raw = raw[:start] + NATIVE + raw[end:]
    terminal = terminal_payload(binding)
    marker = "out=pathlib.Path('/var/lib/pgpt-s1-preservation/" + TERM + "')"
    if terminal.count(marker) != 1:
        raise ValueError('one new terminal guard required')
    raw = constant(raw, 'GUARD', terminal[:terminal.index(marker)])
    oracle = previous.oracle_source().replace('def qualify(old,new,run,cutoff,lower,upper):', 'def qualify_resume(old,new,run,cutoff,lower,upper):')
    oracle += "\ndef qualify(old,new,cutoff,done,upper):\n    require(instant(cutoff)<=instant(done)<=instant(upper))\n    return qualify_resume(old,new,'0dc63b79-3f9a-450c-b2a6-56f86272d272',cutoff," + repr(started) + ",upper)\n"
    raw = constant(raw, 'ORACLE', oracle)
    if old_once['startedUTC'] in raw:
        raise ValueError('old Root observation window leaked')
    if check(raw, '<complete native16 and new Root seal>'):
        raise ValueError('complete current fullseal namespace required')
    compile(raw, '<complete current native16 fullseal>', 'exec')
    return raw


def payload(binding):
    once = json.loads((W / 'pg3122-prepared-browser-resume-once-v1/manifest.safe.json').read_bytes())
    if once['actualExit'] != 0 or once['sourceQualified'] is not True:
        raise ValueError('actual new reserved Root required')
    return rebind(previous.payload(binding), binding, once['startedUTC'])


def main():
    raw = inspect.getsource(previous.main)
    for old, new in [('pg2992-current-resume-terminal-v1', TERM), ('pg2994-current-resume-rows-v1', 'pg3132-browser-resume-rows-v1'), ('pg2990-current-resume-live-binding-v1', 'pg3124-browser-resume-live-binding-v1')]:
        raw = raw.replace(old, new)
    ns = {**previous.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<new all24 and native16 fullseal transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
