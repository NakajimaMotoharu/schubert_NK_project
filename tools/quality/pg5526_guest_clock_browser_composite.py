"""Keep failed5488 mutations explicit; qualify only the new finite guest-clock suffix.

The old host window is NOT repaired or accepted. Its effects are accounted for
under independent Root-seal/new-guest-clock anchors, with exact row continuity.
No old finite-time or formal credit is granted by this preservation bridge.
"""
import ast
import inspect
import json
import types
import pg5490_current_browser_composite as previous
import pg5488_current_same_owner_browser as failed
import pg5524_guest_clock_same_owner_browser as actual
import pg5520_guest_clock_contract as clock
from pg2025_fresh_resume_full_live_seal import constant

admission,root=previous.admission,previous.root
SLOT='pg5526-guest-clock-browser-composite-v1'


def literal(raw,name):
    return next(ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))


def preserved_prefix(old,chain,anchor):
    context=chain['context'];clock.verify_context(context)
    original=old['context']
    if set(original)!={'owner','lower','upper'}or original['owner']!=context['owner']:
        raise ValueError('exact original failed host context and same owner required')
    if old['after']!=chain['before']:
        raise ValueError('failed effects must exactly equal fresh Browser before; no baseline reset')
    if clock.instant(anchor)>clock.instant(context['lower']):raise ValueError('independent guest anchors reversed')
    # A preservation-only envelope: never derived from event timestamps or a
    # measured current offset; original failed context remains an immutable field.
    envelope={'owner':context['owner'],'lower':anchor,'upper':context['lower']}
    clock.qualify(old['before'],old['after'],envelope['owner'],envelope['lower'],envelope['upper'])
    return{'kind':'FAILED_HOST_CLOCK_BROWSER','before':old['before'],'after':old['after'],
        'context':envelope,'originalFailedContext':original,'oldBrowserActualExit':1,
        'oldFiniteTimeWindowQualified':False,'failedCaseNormalized':False}


def compose(raw,chain,digest,prefix):
    base=previous.compose(raw,chain,digest)
    oracle=literal(base,'ORACLE')
    partial='import json\nBROWSER_ORACLE='+repr(literal(oracle,'BROWSER_ORACLE'))+'''
def qualify(old,new,owner,lower,upper):
    ns={};exec(compile(BROWSER_ORACLE,'<unchanged failed-effects data oracle>','exec'),ns)
    result=ns['qualify'](old,new,owner,lower,upper)
    if result['all24Qualified']is not True:raise ValueError('all24 preservation effects rejected')
    return {'all24PartialQualified':True,'oldBrowserActualExit':1,'failedCaseNormalized':False,
        'oldFiniteTimeWindowQualified':False,'coarseEnvelopeOnly':True,'formalAccepted':False}
'''
    oracle=constant(oracle,'PARTIAL_ORACLES',{'FAILED_HOST_CLOCK_BROWSER':partial})
    oracle=constant(oracle,'PARTIAL_CHAIN',[prefix])
    old="if prefixes:require([entry['kind']for entry in prefixes]==['LOGIN_ONLY','AUTH_ADMIN_READ'])"
    if oracle.count(old)!=1:raise ValueError('one exact preserved-prefix policy boundary')
    oracle=oracle.replace(old,"if prefixes:require([entry['kind']for entry in prefixes]==['FAILED_HOST_CLOCK_BROWSER'] and prefixes[0]['oldBrowserActualExit']==1 and prefixes[0]['oldFiniteTimeWindowQualified']is False and prefixes[0]['failedCaseNormalized']is False)",1)
    # The new strict capture contract runs inside the final guest oracle too.
    helper='import datetime\nDOMAIN='+repr(clock.DOMAIN)+'\nSOURCE='+repr(clock.SOURCE)+'\n'+inspect.getsource(clock.instant)+'\n'+inspect.getsource(clock.verify_context)
    target="context=CHAIN['context'];a=datetime.datetime.fromisoformat"
    if oracle.count(target)!=1:raise ValueError('one actual new Browser clock boundary')
    replacement="context=CHAIN['context'];clock_ns={};exec(compile("+repr(helper)+",'<strict captured guest clock>','exec'),clock_ns);clock_ns['verify_context'](context);a=datetime.datetime.fromisoformat"
    oracle=oracle.replace(target,replacement,1)
    # Add truthful preservation metadata without changing Root/Browser oracles.
    target="return {**prefix,'browserAll24Qualified':"
    if oracle.count(target)!=1:raise ValueError('one composite result')
    oracle=oracle.replace(target,"return {'failedBrowserPreserved':True,'failedFiniteTimeWindowQualified':False,'guestClockWindowQualified':True,**prefix,'browserAll24Qualified':",1)
    result=constant(base,'ORACLE',oracle)
    # Only the outer output role changes, never immutable CHAIN/private snapshots.
    old_slot=previous.SLOT
    for name in('SAVE','RAW_SAVE'):
        saves=[n for n in ast.parse(result).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)and old_slot in ast.unparse(n)]
        if len(saves)!=1:raise ValueError('one current output assignment distinct from inherited historical SAVE')
        segment=ast.get_source_segment(result,saves[0])
        if segment.count(old_slot)!=1:raise ValueError('one new-only composite output role')
        result=result.replace(segment,segment.replace(old_slot,SLOT),1)
    if literal(result,'GUARD')!=literal(raw,'GUARD')or literal(oracle,'ROOT_ORACLE')!=literal(raw,'ORACLE')or literal(oracle,'CHAIN')!=chain:
        raise ValueError('immutable Root oracle/guard/new chain drift')
    compile(result,'<strict current Browser chain with explicit failed-effects bridge>','exec')
    return result


def payload(observed):
    proof=json.loads((admission.W/actual.SLOT/'manifest.safe.json').read_bytes())
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['productionSource']==admission.SOURCE and proof['sourceQualified']and proof['passedCases']==12 and proof['all24IndependentPost']and proof['sameFourOrdinaryOwnersBeforeAfter']and proof['guestClockQualified']):
        raise ValueError('new twelve-case coherent guest-clock Browser first')
    cases=admission.W/actual.SLOT/'cases'
    chain={name:json.loads((cases/file).read_bytes())for name,file in [('before','before-rows.private.json'),('after','after-rows.private.json'),('context','context.private.json')]}
    clock.verify_context(chain['context']);clock.qualify(chain['before'],chain['after'],chain['context']['owner'],chain['context']['lower'],chain['context']['upper'])
    old_proof=json.loads((admission.W/failed.SLOT/'manifest.safe.json').read_bytes())
    if not(type(old_proof['actualExit'])is int and old_proof['actualExit']==1 and old_proof['productionSource']==admission.SOURCE and old_proof['sourceQualified']and old_proof['phaseExits']==[0,1]and old_proof['passedCases']==12 and old_proof['sameFourOrdinaryOwnersBeforeAfter']):
        raise ValueError('original failed-clock run must remain an actual failed run')
    old={name:json.loads((admission.W/failed.SLOT/'cases'/file).read_bytes())for name,file in [('before','before-rows.private.json'),('after','after-rows.private.json'),('context','context.private.json')]}
    original=actual.receipt(root.SLOT)
    prefix=preserved_prefix(old,chain,original['observedUpperUtc'])
    return compose(root.payload(observed,admission.before()),chain,original['privateBeforeSha256'],prefix)


def main():
    ns={**vars(previous),'SLOT':SLOT,'payload':payload}
    return types.FunctionType(previous.main.__code__,ns)()


if __name__=='__main__':raise SystemExit(main())
