"""Same-source current certificate/parent18 owned graph; protected data never rebound."""
import inspect
import json
import re
import pg4282_current_owned_sources as previous
import pg3490_outbox_owned_sources as composer
import pg4586_current_independent_acceptance as acceptance
import pg4584_current_admission_image as admission
import pg4648_composite_artifact_requalification as composite
import pg4604_current_same_owner_browser as actual
import pg4650_current_parent_projection as projection
from pg1446_current_cold_stage import W
from immutable_payload_binding import bind_preserving_payloads

SOURCE,BOM=admission.SOURCE,admission.BOM
TOOLS='pg4652-current-owned-tools-v1'


def composite_payload(binding):
    # Generic pre-stop output renaming operates on the actual SAVE assignment,
    # never on protected SQL/history. No old composite is replayed.
    raw=composite.payload()
    marker="base=pathlib.Path('/var/lib/pgpt-s1-preservation');os.umask(0o077);save=base/SLOT;"
    replacement="BASE=pathlib.Path('/var/lib/pgpt-s1-preservation')\nSAVE=BASE/"+repr(composite.SLOT)+"\nbase=BASE;os.umask(0o077);save=SAVE;"
    if raw.count(marker)!=1:raise ValueError('one explicit renameable output boundary')
    return raw.replace(marker,replacement,1)


class Current:
    SOURCE=SOURCE;BOM=BOM;SEAL=composite.SLOT;TERM=acceptance.TERM
    terminal_payload=staticmethod(acceptance.terminal_payload)
    seal_payload=staticmethod(composite_payload)


current=Current


def role_text(raw):
    pairs={previous.TOOLS:TOOLS,previous.SOURCE:SOURCE,previous.BOM:BOM,previous.composite.SLOT:composite.SLOT,
      previous.acceptance.TERM:acceptance.TERM,previous.acceptance.admission.LIVE:admission.LIVE,
      previous.projection.SLOT:projection.SLOT,'PG3976':'PG4432','pg3976':'pg4432',
      'pg4286-current-owned-stage-v1':'pg4656-current-owned-stage-v1','pg4288-current-owned-post-v1':'pg4658-current-owned-post-v1',
      'PG4288-current-owned-post-v1':'PG4658-current-owned-post-v1','pg4282':'pg4652','Pg4282':'Pg4652','PG4282':'PG4652',
      'pg4284':'pg4654','pg4286':'pg4656','pg4287':'pg4657','pg4289':'pg4659'}
    pattern='|'.join(re.escape(k)for k in sorted(pairs,key=len,reverse=True))
    def replace(match):
        token=match.group();first,last=match.span()
        if re.fullmatch('[a-f0-9]{40,64}',token)and((first>0 and raw[first-1]in'0123456789abcdefABCDEF')or(last<len(raw)and raw[last]in'0123456789abcdefABCDEF')):return token
        return pairs[token]
    return re.sub(pattern,replace,raw)


def bind(raw):return bind_preserving_payloads(previous.bind(raw),role_text)


def final_bind(raw):return bind_preserving_payloads(previous.final_bind(raw),role_text)


def candidate_bom():return BOM


def namespace():
    values={**vars(composer),'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'bind':bind,'current':current,'candidate_bom':candidate_bom}
    exec(compile(inspect.getsource(composer.namespace),'<current certified normal owned graph>','exec'),values)
    result=values['namespace']();result['terminal_payload']=acceptance.terminal_payload;return result


def context():
    seal,term=actual.receipt(composite.SLOT),actual.receipt(acceptance.TERM)
    if not(seal['sqlOracleQualified']and seal['currentFourOwnedLive']and seal['newTenRefsNormalClose']and seal['savedThreeImagesRequalified']and term['normalUnit0or10']and seal['businessOracle']['exactRootBrowserCurrentChain']):raise ValueError('actual current independent composite requalification and normal terminal first')
    return seal['privateBeforeSha256'],seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def emit(ctx,binding,state,fields):return {final_bind(n):final_bind(raw)for n,raw in namespace()['emit'](ctx,binding,state,fields).items()}


def sources():
    b=admission.live();binding={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
    term=actual.receipt(acceptance.TERM);p=json.loads((W/projection.SLOT/'manifest.safe.json').read_bytes());ctx=context()
    if p['actualExit']!=0 or p['source']!=SOURCE or p['result']['sealedBeforeSha256']!=ctx[0]:raise ValueError('actual same current parent18 projection')
    return emit(ctx,binding,term['parentState'],p['result']['parentState18'])
