"""Distinct a2ecc unused role over fresh stopped04bb/all80 data; no current startup authority."""
import inspect
import hashlib
import json
import re
from functools import lru_cache
import pg4864_ssc301_302_unused_sources as previous
import pg4916_current_owned_sources as completed
import pg4982_current_preservation_readonly as view
from immutable_payload_binding import bind_preserving_payloads
from pg4968_ssc304_full import SOURCE,W

CURRENT,CURRENT_BOM,BOOT=completed.SOURCE,completed.BOM,previous.BOOT
BEFORE='5ba8f91bcade64a8eedb1bfe51b1e0f99b7d9bd1636b8b9adef131c6ca47436e'
TOOLS='pg4986-ssc304-unused-tools-v1'
SAVE='pg4990-ssc304-unused-placement-v1'
ARCHIVE='pg4990-ssc304-release-v1.tar'
REMOTE='/home/ubuntu/pg4990-ssc304-input-v1'
VIEW_LOCAL=W/view.SLOT/'manifest.safe.json'
BASE,pinned=previous.BASE,previous.pinned
LATEST=W/completed.TOOLS
FACTORY=previous.previous.previous


def candidate_bom():
    value=json.loads((W/'pg4980-candidate-build-v1.safe.json').read_bytes())
    expected={'actualExit':0,'candidateSource':SOURCE,'priorSource':CURRENT,'signatureVerified':True,
        'candidateNotDeployed':True,'formalAccepted':False,'allSixFormatBeforeAnyPt':True,'manifestSha256':view.CANDIDATE_BOM}
    if any(type(value.get(k))is not type(v)or value[k]!=v for k,v in expected.items()):raise ValueError('actual distinct signed SSC304 candidate')
    return value['manifestSha256']


def production():return SOURCE


def qualify():
    outer=json.loads(VIEW_LOCAL.read_bytes());v=outer['result'];candidate_bom()
    expected={'actualExit':0,'productionSource':CURRENT,'freshCurrentPreservation':True,
        'whole24Full32Signed187AndResourcesUnchanged':True,'allResources0':True,'normalNewReferences':True,
        'capturedNormal20VerifiedBeforeCurrent':True,'bootstrapCredentialsAbsent':True,'currentCredentialsRetired':True,
        'nativePhysicalFiles':80,'privateBeforeSha256':BEFORE,'sealedFull11Fields':11,
        'dataOnlyNotRuntimeAuthority':True,'nativeCandidateCredit':False,'candidateDeployed':False,
        'candidateSource':SOURCE,'candidateBOM':candidate_bom()}
    if type(outer['actualExit'])is not int or outer['actualExit']!=0 or outer['source']!=CURRENT:
        raise ValueError('actual fresh current04bb reader first')
    if any(type(v.get(k))is not type(x)or v[k]!=x for k,x in expected.items()):raise ValueError('all actual current80/data-only criteria')
    if hashlib.sha256(view.payload().encode()).hexdigest()!=outer['payloadSha256']:
        raise ValueError('exact full current reader includes active/intent absence; no boolean invention')


def normalized_text(raw):
    pairs={previous.CURRENT:CURRENT,previous.SOURCE:SOURCE,previous.CURRENT_BOM:CURRENT_BOM,
        previous.candidate_bom():candidate_bom(),previous.BEFORE:BEFORE,
        'PG4860':'PG4980','pg4860':'pg4980','PG4702':'PG4860','pg4702':'pg4860',
        previous.view.SLOT:view.SLOT,previous.TOOLS:TOOLS,previous.SAVE:SAVE,previous.ARCHIVE:ARCHIVE,previous.REMOTE:REMOTE,
        'pg4864':'pg4986','Pg4864':'Pg4986','PG4864':'PG4986','pg4866':'pg4988','PG4866':'PG4988',
        'pg4868':'pg4990','PG4868':'PG4990','pg4870':'pg4992','PG4870':'PG4992'}
    pattern='|'.join(re.escape(k)for k in sorted(pairs,key=len,reverse=True))
    def replace(match):
        token=match.group();first,last=match.span()
        if re.fullmatch('[a-f0-9]{40,64}',token)and((first and raw[first-1]in'0123456789abcdefABCDEF')or(last<len(raw)and raw[last]in'0123456789abcdefABCDEF')):return token
        return pairs[token]
    return re.sub(pattern,replace,raw)


def role_text(raw):return normalized_text(previous.role_text(raw))


@lru_cache(maxsize=1)
def current_tuple():
    raw=inspect.getsource(previous.previous.current_tuple.__wrapped__).replace('pg4652_parent_receipt.py','pg4916_parent_receipt.py')
    ns={**vars(previous.previous),'LATEST':LATEST,'completed':completed,'BOOT':BOOT}
    exec(compile(raw,'<actual closed04bb current tuple; history only>','exec'),ns)
    return ns['current_tuple']()


def native_refs(raw):
    base=previous.previous.previous.previous
    ns={**vars(base),'current_tuple':current_tuple}
    exec(compile(inspect.getsource(base.native_refs),'<actual current04bb reference data>','exec'),ns)
    result=ns['native_refs'](raw)
    marker="'unitFilesActual': file_entries, 'runtime': runtime}"
    if result.count(marker)!=1:raise ValueError('one full capture with actual all80 native')
    result=result.replace(marker,"'unitFilesActual': file_entries, 'runtime': runtime, 'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}",1)
    marker="require(not pathlib.Path('/proc/225062').exists())"
    root=completed.admission.live()['rootPid']
    if result.count(marker)!=1 or type(root)is not int or root!=882496:raise ValueError('one actual retired04bb Root generation')
    return result.replace(marker,"require(not pathlib.Path('/proc/"+str(root)+"').exists())",1)


def latest_alias(raw):return bind_preserving_payloads(raw,lambda value:value.replace('pg4916','pg4986').replace('PG4916','PG4986'))


def sources(bom=None,before=None):
    qualify();actual=candidate_bom()
    if bom is not None and bom!=actual or before is not None and before!=BEFORE:raise ValueError('exact current04bb/candidatea2ecc data role')
    ns={**vars(FACTORY),'CURRENT':CURRENT,'CURRENT_BOM':CURRENT_BOM,'SOURCE':SOURCE,'BOM':actual,
        'BEFORE':BEFORE,'BOOT':BOOT,'TOOLS':TOOLS,'SAVE':SAVE,'ARCHIVE':ARCHIVE,'REMOTE':REMOTE,
        'BASE':BASE,'LATEST':LATEST,'qualify':qualify,'role_text':role_text,'current_tuple':current_tuple,
        'native_refs':native_refs,'latest_alias':latest_alias,'candidate_bom':candidate_bom}
    raw=inspect.getsource(FACTORY.sources)
    for old,new in(('pg3982','pg4986'),('Pg3982','Pg4986'),('PG3982','PG4986'),
                    ('pg3876','pg4916'),('Pg3876','Pg4916'),('PG3876','PG4916')):raw=raw.replace(old,new)
    exec(compile(raw,'<all18 distinct current04bb/candidatea2ecc roles>','exec'),ns)
    return ns['sources']()


if __name__=='__main__':raise SystemExit('pure factory; no guest action')
