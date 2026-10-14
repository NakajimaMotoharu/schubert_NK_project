"""Current fresh resume: raw-before preserved, sealed same-source native anchor added in memory."""
import inspect
import json
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg2368_current_resume_full_seal as previous
from pg2025_fresh_resume_full_live_seal import constant
from pg2992_current_resume_terminal import payload as terminal_payload, SLOT as TERM
from pg2366_current_resume_rows import oracle_source
from pg2982_current_resume_observer import SOURCE, BOM

SLOT = 'pg3000-current-resume-full-seal-v1'

NATIVE_ANCHOR = r'''
def native_before_anchor(before):
 p=BASE/'pg2964-retained-full-pair-proof-v1/proof.private.json';s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()=='c1170b22495c28a114640f2f1153c92c9fa673431b0fc35e4e0039d0ca9cb510')
 anchor=json.loads(raw);require(anchor['signals0']is True and anchor['all24And187OriginalBackupUnchanged']is True)
 native_before=anchor['native']
 require(hashlib.sha256(json.dumps(native_before,sort_keys=True).encode()).hexdigest()=='96757f38127024e527c5356308e1d6337fb1bb50b2e258283bf2d2fc00376423')
 copied=BASE/'pg2984-current-fresh-resume-once-v1/native-before-private'
 manifest=json.loads((copied.parent/'native-before-manifest.private.json').read_bytes())
 expected={str(pathlib.Path(k).relative_to('/run/schubert-nk/pt-coverage')):{'sha256':v['sha256'],'bytes':v['metadata'][6]}for k,v in native_before.items()if k.endswith('.exec')}
 require(manifest==expected and len(manifest)==10)
 for name,value in manifest.items():
  p=copied/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p)and s.st_size==value['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256'])
 return {**before,'native':native_before}
before=native_before_anchor(before);require(before_shape(before))
'''


def payload(binding):
    raw = previous.payload(binding)
    # Replace complete nested contracts separately; never generic-rebind their
    # historical forbidden tuple guards into a positive current tuple.
    raw = constant(raw, 'GUARD', 'CURRENT_GUARD_INSERTED_BELOW')
    raw = constant(raw, 'ORACLE', 'CURRENT_ORACLE_INSERTED_BELOW')
    for a, b in [(previous.SLOT, SLOT), ('pg2360-current-completed-resume-once-v1', 'pg2984-current-fresh-resume-once-v1'), (previous.SOURCE, SOURCE), (previous.BOM, BOM), ('6873c5eb138bbd3dbd6a8e00398738b837dca149325db0ff555d0901bd1b10ec', 'd10735e678e5053c0c96c55a42f65f2302132cfae902edd81dffbc2275c4c4ac'), ('b2d6f605-61cf-425f-8fbd-12d606f6ee66', '79a3260a-e16d-42bf-942a-b914ed144c28'), ('PG2126', 'PG2802'), ('pg2126', 'pg2802'), ('91f5484b-9702-4c7c-97f3-dd5110a853f9', '0dc63b79-3f9a-450c-b2a6-56f86272d272'), ('2026-10-13T15:01:53.237266Z', '2026-10-14T19:12:28.842213Z')]:
        raw = raw.replace(a, b)
    start = raw.index("native_post_raw=(BASE/'pg2356-current-runtime-verification-post-v1/after.private.json')")
    end_marker = "before['native']=native_post['native'];require(before_shape(before))"
    end = raw.index(end_marker, start) + len(end_marker)
    raw = raw[:start] + NATIVE_ANCHOR + raw[end:]
    terminal = terminal_payload(binding)
    marker = "out=pathlib.Path('/var/lib/pgpt-s1-preservation/" + TERM + "')"
    if terminal.count(marker) != 1:
        raise ValueError('one complete current terminal guard required')
    raw = constant(raw, 'GUARD', terminal[:terminal.index(marker)])
    once = json.loads((W / 'pg2984-current-fresh-resume-once-v1/manifest.safe.json').read_bytes())
    oracle = oracle_source().replace('def qualify(old,new,run,cutoff,lower,upper):', 'def qualify_resume(old,new,run,cutoff,lower,upper):')
    oracle += "\ndef qualify(old,new,cutoff,done,upper):\n    require(instant(cutoff)<=instant(done)<=instant(upper))\n    return qualify_resume(old,new,'0dc63b79-3f9a-450c-b2a6-56f86272d272',cutoff," + repr(once['startedUTC']) + ",upper)\n"
    raw = constant(raw, 'ORACLE', oracle)
    if check(raw, '<whole current resume full seal>'):
        raise ValueError('complete current seal namespace required')
    compile(raw, '<whole current resume full seal>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.previous.prior.previous.previous.main)
    for a, b in [('pg2021-fresh-resume-terminal-receipt-v1', 'pg2992-current-resume-terminal-v1'), ('pg2023-fresh-resume-rows-oracle-v1', 'pg2994-current-resume-rows-v1'), ('pg2019-fresh-resume-live-binding-complete-v1', 'pg2990-current-resume-live-binding-v1')]:
        raw = raw.replace(a, b)
    raw = raw.replace("payload(live['binding'])", "payload({**live['binding'],'rootPid':live['rootPid']})")
    ns = {**previous.previous.prior.previous.previous.__dict__, 'SLOT': SLOT, 'SOURCE': SOURCE, 'BOM': BOM, 'payload': payload}
    exec(compile(raw, '<current full seal actual dispatcher>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
