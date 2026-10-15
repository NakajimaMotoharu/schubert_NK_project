"""Private-systemctl syscall witness plus separate whole-post, successful v4 only."""
import pg3226_legacy_negative_post as previous
from pg1446_current_cold_stage import W


def build():
    raw = previous.CODE
    for old, new in [('pg3224-legacy-negative-v1', 'pg3230-legacy-negative-v1'), ('cohort-v3', 'cohort-v4'),
                     ('cohort-native-v3.exec', 'cohort-native-v4.exec'), ('PG3222-LFACT-v3', 'PG3230-LFACT-v4')]:
        if old not in raw: raise ValueError('one exact previous scope required: ' + old)
        raw = raw.replace(old, new)
    old = "o.require([x['member']for x in mutations]==['StartUnit','StopUnit']and all(x['payload']['data']==[o.UNIT,'replace']for x in mutations))"
    if raw.count(old) != 1: raise ValueError('old incorrect public-bus scope boundary required')
    raw = raw.replace(old, "o.require(mutations==[])\nsyscalls=(root/'syscall.private.log').read_bytes()\no.require(whole['privateSystemctlExecVerified']is True and whole['publicBusScopeLimited']is True and hashlib.sha256(syscalls).hexdigest()==whole['syscallSha256'])\no.traced_calls(syscalls.decode('utf-8'))")
    raw = raw.replace("files={'runtime-input.safe.json':meta}", "files={'runtime-input.safe.json':meta,'syscall.private.log':syscalls}")
    raw = raw.replace("v['approvalAccessObserved']and a['source']==o.SOURCE)", "v['approvalAccessObserved']and a['source']==o.SOURCE and v['actualSystemctlShowExecs']>0 and v['unsafeSystemctlExecs']==0 and v['helperAllThreadAndDescendantSyscallTrace']is True and v['inetConnects']==0)")
    return raw


if __name__ == '__main__':
    previous.OUT = W / 'pg3232-legacy-negative-post-v1'
    previous.EXECUTION_SLOT = 'pg3230-legacy-negative-v1'
    previous.CODE = build()
    previous.main()
