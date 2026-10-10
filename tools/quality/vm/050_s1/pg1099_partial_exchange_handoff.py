"""SSC251 fixed once retirement only; old activation never becomes successful."""
import ast
import json
from pathlib import Path
from pg1098_partial_exchange_preflight import payload as previous,CHILD_ARGV
from pg1060_cold_owned_tree_handoff import HANDOFF as previous_handoff
from pg1041_cold_policy_diagnostic import W
from pg1051_cold_tree_preflight_v2 import dispatch


def handoff():
    raw=previous_handoff
    for old,new in [('5463','16222'),('5489','16248'),('1373880','3020295'),('1373951','3020358'),
        ('8067bb56195ab7f05b1427a9d5cf78f5d71e404000acc5f5f3391c5079e5a1d9',CHILD_ARGV),
        ('pg1037-cold-prepared-v1/tree-preflight-v4','pg1094-cold-activate-v1/partial-preflight-v1'),
        ("('snapshot','controls','heldWholeMetadata')","('snapshot','controls','heldWholeMetadata','runtime','partialTrees')")]:
        raw=raw.replace(old,new)
    raw=raw.replace("'heldWholeMetadata':safe([h.capture()for h in held[:CORE_COUNT]])}",
                    "'heldWholeMetadata':safe([h.capture()for h in held[:CORE_COUNT]]),'runtime':runtime(),'partialTrees':partial_state()}")
    return raw


def payload():
    result=json.loads((W/'pg1098-partial-exchange-preflight-v1/manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or not result['observed']['observerNormalClose']:raise ValueError('qualified fixed partial preflight required')
    raw=previous().replace('PG1098-partial-exchange-preflight-v1','PG1099-partial-exchange-handoff-v1')
    raw=raw.replace("save=OLD_SAVE/'partial-preflight-v1'","save=OLD_SAVE/'partial-preflight-v1/owned-handoff-v1'")
    raw=raw.replace("held=[];refs=[];bus=None;manager=None;phase='ENTRY';old_approval_fd=None", "held=[];refs=[];bus=None;manager=None;phase='ENTRY';old_approval_fd=None\nRESERVATION_ATTEMPTED=False;SIGNAL_ATTEMPTED=False;SIGNAL_COUNT=0;reservation_fd=None;CORE_COUNT=0\nimport signal,select\ntree_contract=module('once_tree',TREE_SOURCE)")
    # The durable qualification file is additional to the original core held set.
    raw=raw.replace("safe([h.capture()for h in held])", "safe([h.capture()for h in held[:CORE_COUNT or len(held)]])")
    marker='def read():\n'
    helper="""def partial_state():
 trees={r:io.direct_tree(r)for r in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)}
 partial.partial(original_before['trees'],trees,epoch,begin_ns,time.time_ns())
 row=original_before['trees'][pub.APPROVAL][pub.APPROVAL+'/current']
 pub.verify_retained(pub.APPROVAL+'/current',row,io.fd_record(old_approval_fd),'after',trees,begin_ns,time.time_ns())
 return trees
"""
    if raw.count(marker)!=1:raise ValueError('fixed partial handoff helper insertion refused')
    raw=raw.replace(marker,helper+marker)
    start=" phase='WHOLE_TWO_READ';before=read();assert before==read();before['childBusUniqueName']=child_names[0]"
    end=" phase='NORMAL_CLOSE'"
    if raw.count(start)!=1 or raw.count(end)!=1:raise ValueError('fixed partial handoff phase refused')
    raw=raw[:raw.index(start)]+handoff()+raw[raw.index(end):]
    raw=raw.replace('proof=pin_file(prior,PRIOR_SHA)','proof=pin(prior,PRIOR_SHA)')
    t=ast.parse(raw)
    t.body[-1]=ast.parse("print(json.dumps({'run':'PG1099-partial-exchange-handoff-v1','actualExit':0,'oldParentGone':True,'oldChildGone':True,'oldBusGone':True,'oldClientsAdvisoryFlocks0':True,'allOriginalsUnchangedTwice':True,'partialPublicationUnchanged':True,'observerNormalClose':True,'oldOperationNormalClose':False,'oldTransportExit':None,'signalsAttempted':SIGNAL_COUNT,'reservationDurable':True,'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'afterPrivateSha256':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),'formalAccepted':False}))").body[0]
    return 'PRIOR_SHA='+repr(result['observed']['beforePrivateSha256'])+'\nTREE_SOURCE='+repr(Path(__file__).with_name('pg1049_cold_tree_contract.py').read_text())+'\n'+ast.unparse(t)


if __name__=='__main__':dispatch('PG1099-partial-exchange-handoff-v1','pg1099-partial-exchange-handoff-v1',payload())
