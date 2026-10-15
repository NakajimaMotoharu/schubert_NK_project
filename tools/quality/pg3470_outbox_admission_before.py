"""Read-only immutable once-admission image qualification; no live DB or start."""
import inspect
import json
import pg2698_operation_admission_before as old
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg3462_outbox_current_observer import SOURCE
from pg3464_outbox_current_noargs_once import SLOT as ONCE
from pg3466_outbox_current_live_binding import SLOT as LIVE
from pg478_cleanup_oracle import candidates, instant, older
from pg1766_next_day_independent_candidates import classify_inbox

SLOT = 'pg3470-outbox-admission-before-v1'
BODY = old.BODY.replace('pg2684-operation-current-noargs-once-v2', ONCE)
BODY = BODY.replace("require(len(v['native'])==41 and sum(pathlib.Path(k).suffix=='.exec'for k in v['native'])==28)", """post=pathlib.Path('/var/lib/pgpt-s1-preservation/pg3458-current-outbox-publication-independent-post-v1/after.private.json')
post_raw=post.read_bytes();require(hashlib.sha256(post_raw).hexdigest()=='745b9c300446e11bd4230df34617f0bbf8ed738c8ea457ed2d107cd515aa717e')
expected=json.loads(post_raw)
require(v['native']==expected['native']and {k:x for k,x in v.items()if k!='native'}==expected['after'])
require(sum(pathlib.Path(k).suffix=='.exec'for k in v['native'])==22)""")
BODY = BODY.replace("'nativeEntries':41,'execEntries':28", "'nativeEntries':len(v['native']),'execEntries':22")


def payload():
    live = json.loads((W / LIVE / 'manifest.safe.json').read_bytes())
    if live['actualExit'] != 0 or live['productionSource'] != SOURCE:
        raise ValueError('actual same new Root before selectors required')
    prefix = 'import datetime\nUTC=datetime.timezone.utc\nCUT=' + repr(live['binding']['cutoff']) + '\n'
    prefix += '\n'.join(inspect.getsource(f) for f in [instant, older, candidates, classify_inbox]) + '\n'
    marker = "print(json.dumps({'actualExit':0,"
    if BODY.count(marker) != 1:
        raise ValueError('one actual immutable admission output boundary')
    raw = BODY[:BODY.index(marker)]
    raw += """
expected=candidates(v['rows'],CUT);inbox=classify_inbox(v['rows'],expected['inbox_scan_candidates'])
day=instant(CUT).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
require(day=='2026-10-16' and not any(r['business_date']==day for r in v['rows']['schubert.batch_runs']))
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg3470-outbox-admission-before-v1');require(not os.path.lexists(out));out.mkdir(mode=0o700)
oracle={'cutoff':CUT,'businessDate':day,'beforeSha256':hashlib.sha256(raw).hexdigest(),'expected':expected,'expectedInbox':inbox}
encoded=json.dumps(oracle,sort_keys=True).encode()
with(out/'oracle.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [out,out.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'nativeEntries':len(v['native']),'execEntries':22,'oracleSha256':hashlib.sha256(encoded).hexdigest(),'candidateCounts':{k:len(x)for k,x in expected.items()},'expectedInboxProtected':len(inbox['protected']),'businessDate':day,'sameDayHistoryCount':0,'rawExported':False,'productionCalls':0,'actualDbRowsRead':0}))
"""
    # Guest raw above is the immutable before-image bytes, not this source text.
    result = prefix + raw
    if check(result, '<complete actual before selector namespace>'):
        raise ValueError('complete immutable selector namespace required')
    compile(result, '<independent before selectors, no live DB>', 'exec')
    return result


def before():
    v = json.loads((W / SLOT / 'manifest.safe.json').read_bytes())
    if type(v.get('actualExit')) is not int or v['actualExit'] != 0 or v.get('productionSource') != SOURCE:
        raise ValueError('actual same source independent admission hash required')
    return v['guest']['privateBeforeSha256']


def main():
    raw = inspect.getsource(old.main).replace('pg2684-operation-current-noargs-once-v2', ONCE)
    raw = raw.replace('pg2686-operation-current-live-binding-v1', LIVE)
    ns = {**old.__dict__, 'SLOT': SLOT, 'BODY': payload(), 'production': lambda: SOURCE}
    exec(compile(raw, '<current4856 actual immutable before qualifier>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
