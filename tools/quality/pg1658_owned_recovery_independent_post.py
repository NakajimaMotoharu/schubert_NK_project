"""Separate full current/Original/native/resource post after SSC273 handoff."""
import inspect
import json
import pg1641_completed_current_preflight_v2 as prior

SLOT = 'pg1658-owned-recovery-independent-post-v1'
FRESH = '7ed5bfcaf22c91a1075a1286b63b682dcd4df40ac2b5cd2528c2cc210e97a8a9'

EXTRA = r'''
require(not pathlib.Path('/proc/289328').exists())
handoff=base/'pg1657-same-connection-fresh-handoff-v1'
names={'proof-before.private.json','fresh-proof.private.json','fresh-complete.private','289328.term-once.private','post.private.json','complete.private'}
require({p.name for p in handoff.iterdir()}==names)
def held_private(name):
 p=handoff/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return raw
require(hashlib.sha256(held_private('proof-before.private.json')).hexdigest()=='6297a9d8efb937b67a480f67051efa5907207ed14c257df2b36605ab3a4839bb')
fresh_raw=held_private('fresh-proof.private.json');require(hashlib.sha256(fresh_raw).hexdigest()==FRESH)
fresh=json.loads(fresh_raw);require(fresh['signalsIssued']==0 and fresh['independentFreshProofComplete']is True and fresh['allOriginalValuesUnchanged']is True and fresh['native']==native)
require(held_private('fresh-complete.private')==('independentFreshProofComplete=true\nsignalsIssued=0\nproofSha256='+FRESH+'\n').encode())
reservation=json.loads(held_private('289328.term-once.private'));require(reservation['pid']==289328 and reservation['ticks']==5627480 and reservation['signal']=='TERM'and reservation['replayAllowed']is False and reservation['actor']==fresh['actor'])
post=json.loads(held_private('post.private.json'));require(post['native']==native and post['originalAfterSha256']=='9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37'and all(post[k]is True for k in ['all24And32And187Unchanged','allTenKernelEmpty','clientAdvisoryFlock0','ownedActorGone','candidateNotPlaced','oldCloseUnknown']))
require(held_private('complete.private')==b'ownedJavaGone=true\nallOriginalValuesUnchanged=true\nallOldResources0=true\nnewRefScopeNormal=true\noldCloseUnknown=true\n')
require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())
'''


def payload():
    raw = prior.payload().replace('pg1641-completed-current-before-v2', SLOT)
    marker = "save=base/'" + SLOT + "'"
    if raw.count(marker) != 1:
        raise ValueError('one separate full current post boundary required')
    raw = 'FRESH=' + repr(FRESH) + '\n' + raw.replace(marker, EXTRA + '\n' + marker)
    raw = raw.replace("'rawExported':False", "'ownedRecoveryIndependentPost':True,'oldCloseUnknown':True,'rawExported':False")
    compile(raw, '<separate full owned recovery post>', 'exec')
    return raw


def main():
    v = json.loads((prior.prior.W / 'pg1657-same-connection-fresh-handoff-v1/manifest.safe.json').read_bytes())
    if v['actualExit'] != 0 or v['guest']['freshProofSha256'] != FRESH or v['guest']['oldCloseUnknown'] is not True:
        raise ValueError('actual fixed single handoff completion required')
    code = inspect.getsource(prior.prior.main).replace('pg1639-completed-current-before-v1', SLOT)
    ns = {**prior.prior.__dict__, 'payload': payload}
    exec(compile(code, '<new separate full post transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
