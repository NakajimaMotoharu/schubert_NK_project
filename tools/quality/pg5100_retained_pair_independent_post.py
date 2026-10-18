"""Independent all-original/resource post, also fresh enriched baseline for new-only retry."""
import ast
import hashlib
import json
from pyflakes.api import check
import pg5080_current_bootstrap_before as before
import pg5082_current_bootstrap_sources as role
import pg5096_retained_pair_once_recovery as recovery

SLOT = 'pg5100-retained-pair-independent-post-v1'
SOURCE, BOM, AFTER, admission = before.SOURCE, before.BOM, before.AFTER, before.admission

BODY = r'''
require(not pathlib.Path('/proc/927504').exists()and not pathlib.Path('/proc/927536').exists())
handoff=base/'pg5096-retained-pair-once-recovery-v1'
require({p.name for p in handoff.iterdir()}=={'proof.private.json','original-proof.private.json','fresh-complete.private','927536.term-once.private','927504.term-once.private','post.private.json','complete.private'})
def recovery_read(name):return strict(handoff/name,0o600,67108864)
fresh_raw=recovery_read('proof.private.json');require(hashlib.sha256(fresh_raw).hexdigest()==FRESH)
fresh=json.loads(fresh_raw);require(fresh['productionSource']==SOURCE and fresh['signals0']is True and fresh['oldCloseUnknown']is True and fresh['native']==native)
require(hashlib.sha256(recovery_read('original-proof.private.json')).hexdigest()=='f0496ff80babbe6aa7a1926193739436a8170c3d22c835dd205cc749e85cc1db')
require(recovery_read('fresh-complete.private')==('freshReadOnlyProofComplete=true\nsignalsIssued=0\nproofSha256='+FRESH+'\n').encode())
child=json.loads(recovery_read('927536.term-once.private'));parent=json.loads(recovery_read('927504.term-once.private'))
for v,pid,ticks in [(child,927536,31055311),(parent,927504,31055084)]:
 require(set(v)=={'pid','ticks','actor','signal','replayAllowed'}and v['pid']==pid and v['ticks']==ticks and v['signal']=='TERM'and v['replayAllowed']is False)
require(child['actor']==fresh['pair']['child'])
pipes={fresh['pair']['child']['fds'][n]['target']for n in ['0','1']};require(parent_after_ref(fresh['pair']['parent'],parent['actor'],pipes))
post=json.loads(recovery_read('post.private.json'));require(post=={'native':native,'oldCloseUnknown':True,'allOriginalValuesUnchanged':True,'allOldResources0':True,'ownedParentAndChildGone':True})
require(recovery_read('complete.private')==b'ownedParentAndChildGone=true\noldCloseUnknown=true\nallOldResources0=true\nfullIndependentPostPending=true\n')
require(hashlib.sha256(snapshot_raw).hexdigest()==BASELINE)
'''


def prerequisites():
    outer = json.loads((admission.W / recovery.SLOT / 'manifest.safe.json').read_bytes())
    old = json.loads((admission.W / 'pg5086-current-bootstrap-verify-v1.safe.json').read_bytes())
    stages = outer.get('stages', [])
    if not (type(outer.get('actualExit')) is int and outer['actualExit'] == 0
            and outer.get('productionSource') == SOURCE and outer.get('criticalGateNormallyInherited') is True
            and len(stages) == 2 and stages[0].get('signalsIssued') == 0
            and stages[1].get('ownedTermSignals') == 2
            and all(stages[1].get(k) is True for k in ('ownedParentAndChildGone','allOldResources0','allOriginalValuesUnchanged','normalNewRefScope','oldCloseUnknown','fullIndependentPostPending'))
            and type(old.get('actualExit')) is int and old['actualExit'] == 143
            and old.get('productionSource') == SOURCE and old.get('action') == 'verify'
            and hashlib.sha256((admission.W/recovery.SLOT/'payload.private.py').read_bytes()).hexdigest() == outer['payloadSha256']):
        raise ValueError('same actual owned recovery and original143 before independent post')
    return stages[0]['proofSha256']


def payload():
    import inspect
    from pg1665_unused_pair_contract import parent_after_ref
    fresh = prerequisites()
    tree = ast.parse(before.payload())
    scope = next(n for n in tree.body if isinstance(n,ast.Try) and n.finalbody
                 and any(isinstance(v,ast.FunctionDef)and v.name=='snapshot'for v in n.body))
    # Only new output namespace; every original guard/function remains intact.
    target = next(n for n in scope.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='save'for t in n.targets))
    target.value = ast.parse('base/'+repr(SLOT),mode='eval').body
    scope.body += ast.parse(BODY).body
    result = tree.body[-1]
    raw = ast.unparse(result)
    marker="'formalAccepted': False"
    if raw.count(marker)!=1:
        raise ValueError('one outgoing post qualification')
    raw=raw.replace(marker,"'allResources0': True, 'ownedPairRecoveryComplete': True, 'oldCloseUnknown': True, 'retainedVerifyActualExit': 143, "+marker)
    tree.body[-1]=ast.parse(raw).body[0]
    raw='FRESH='+repr(fresh)+'\nBASELINE='+repr(role.BASELINE)+'\n'+inspect.getsource(parent_after_ref)+'\n'+ast.unparse(ast.fix_missing_locations(tree))+'\n'
    if check(raw,'<independent recovered same24/32/187/86 all resources>'):
        raise ValueError('complete independent post globals')
    return raw


if __name__=='__main__':
    raise SystemExit(admission.execute(SLOT,payload(),180))
