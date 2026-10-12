"""SSC275 independent full current post; no signal or service capability."""
import inspect
import json
import re
import hashlib
import pg1641_completed_current_preflight_v2 as prior
from pg1446_current_cold_stage import W

SLOT = 'pg1675-remaining-owner-full-post-v1'

EXTRA = r'''
require(not pathlib.Path('/proc/291213').exists()and not pathlib.Path('/proc/291242').exists())
handoff=base/'pg1674-remaining-owner-handoff-v1'
require({p.name for p in handoff.iterdir()}=={'old-proof.private.json','fresh-proof.private.json','fresh-complete.private','291213.term-once.private'})
def held_private(name):
 p=handoff/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return raw
require(hashlib.sha256(held_private('old-proof.private.json')).hexdigest()=='537aaccf3ff3f98e17e71dbda28fa7bfe671e44699f9b7d59c6fde9241dd93aa')
raw=held_private('fresh-proof.private.json');require(hashlib.sha256(raw).hexdigest()==FRESH)
fresh=json.loads(raw);require(fresh['signalsIssued']==0 and fresh['independentFreshProofComplete']is True and fresh['allOriginalValuesUnchanged']is True and fresh['childAlreadyReaped']is True and fresh['native']==native)
require(held_private('fresh-complete.private')==('independentFreshProofComplete=true\nsignalsIssued=0\nproofSha256='+FRESH+'\n').encode())
reservation=json.loads(held_private('291213.term-once.private'));require(reservation['pid']==291213 and reservation['ticks']==5962776 and reservation['actor']==fresh['actor']and reservation['signal']=='TERM'and reservation['replayAllowed']is False)
require(not(handoff/'complete.private').exists())
require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())
'''


def payload(fresh):
    if type(fresh) is not str or re.fullmatch('[0-9a-f]{64}', fresh) is None:
        raise ValueError('actual fresh proof digest required')
    raw=prior.payload().replace('pg1641-completed-current-before-v2',SLOT)
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one separate full post boundary required')
    raw='FRESH='+repr(fresh)+'\n'+raw.replace(marker,EXTRA+'\n'+marker)
    raw=raw.replace("'rawExported':False", "'soleOwnerIndependentPost':True,'oldReapInterrupted':True,'oldCloseUnknown':True,'rawExported':False")
    compile(raw,'<separate sole owner complete original post>','exec')
    return raw


def qualify_interrupted_reap():
    actual=json.loads((W/'pg1674-remaining-owner-handoff-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=1 or len(actual['stages'])!=1:raise ValueError('actual interrupted reap preserved required')
    first=actual['stages'][0]
    if first['signalsIssued']!=0 or first['proofSha256']!='8a5b856fc239b72a65aed0710212ee4829d78a8914d7734dd3dc5abee387bc26':raise ValueError('exact signals0 fresh proof required')
    source=(W/'pg1674-remaining-owner-handoff-v1/payload.private.py').read_bytes()
    if hashlib.sha256(source).hexdigest()!='6d3e2c8f1785733a4da089ed9b9721336adfa67cf0b0d461bf2152083fe5a47b':raise ValueError('actual fixed interrupted source required')
    lines=source.decode().splitlines()
    if "terminate(291213,5962776,before,reserve,os.pidfd_open,send,wait,os.close)" not in '\n'.join(lines[:414]) or "pathlib.Path('/proc/291213/stat').read_text()" not in lines[414]:raise ValueError('proc read must follow onceTERM and finitewait')
    error=(W/'pg1674-remaining-owner-handoff-v1/stderr.private.log').read_text()
    if 'line 415, in <module>' not in error or not error.rstrip().endswith('ProcessLookupError: [Errno 3] No such process'):raise ValueError('actual ESRCH at exact finite reap required')
    # No successful cleanup is inferred here: full guest original/resource post
    # must independently pass, and old exit1 / missing complete stay unchanged.
    return first['proofSha256']


def main():
    fresh=qualify_interrupted_reap()
    code=inspect.getsource(prior.prior.main).replace('pg1639-completed-current-before-v1',SLOT)
    ns={**prior.prior.__dict__,'payload':lambda:payload(fresh)}
    exec(compile(code,'<separate full current post transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
