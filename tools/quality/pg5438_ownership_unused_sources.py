"""Distinct candidate296 unused18 over fresh currentA2 full11/native88; no start authority."""
import inspect
import json
import re
import types
from functools import lru_cache
import pg5436_current_full11_view as view
import pg4986_ssc304_unused_sources as previous
import pg3756_hygiene_unused_sources as original
import pg5060_current_owned_sources as completed
from immutable_payload_binding import bind_preserving_payloads

W=view.W
CURRENT,CURRENT_BOM,CANDIDATE=view.before.CURRENT,view.before.CURRENT_BOM,view.before.CANDIDATE
SOURCE=CANDIDATE
BEFORE='ea4a5469d654650e85af68713550b8d9e1f676910b50ca26a33286e29c84f283'
BOOT=previous.BOOT
TOOLS='pg5438-ownership-unused-tools-v1'
SAVE='pg5442-ownership-unused-placement-v1'
ARCHIVE='pg5442-ownership-release-v1.tar'
REMOTE='/home/ubuntu/pg5442-ownership-input-v1'
VIEW_LOCAL=W/view.SLOT/'manifest.safe.json'
BASE,pinned=previous.BASE,previous.pinned
LATEST=W/completed.TOOLS


def candidate_bom():
    value=json.loads((W/'pg5430-candidate-build-v1.safe.json').read_bytes())
    expected={'actualExit':0,'candidateSource':SOURCE,'priorSource':CURRENT,'signatureVerified':True,
        'candidateNotDeployed':True,'formalAccepted':False,'allSixFormatBeforeAnyPt':True,
        'manifestSha256':'85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6'}
    if any(type(value.get(k))is not type(v)or value[k]!=v for k,v in expected.items()):
        raise ValueError('actual distinct qualified signed296 host candidate')
    return value['manifestSha256']


def production():return SOURCE


def qualify():
    candidate_bom();outer=json.loads(VIEW_LOCAL.read_bytes());v=outer['result']
    expected={'actualExit':0,'productionSource':CURRENT,'BOM':CURRENT_BOM,'privateBeforeSha256':BEFORE,
        'sealedFull11Fields':11,'tables':24,'unitCount':10,'nativePhysicalFiles':88,
        'snapshotSha256':'4ab25ad070358ef6580a29855c2cbd1fe00f9cb32f6a514bc279a932bcd0ba94',
        'snapshotOrigin':view.before.SLOT,'snapshotReadTimeIsOriginal5434':True,'newDatabaseReads':0,
        'currentOriginalClosedAndNoIntent':True,'runtimeConfigFilesToRetire':0,
        'dataOnlyNotRuntimeAuthority':True,'nativeCandidateCredit':False,'formalAccepted':False}
    if type(outer['actualExit'])is not int or outer['actualExit']!=0 or outer['source']!=CURRENT:
        raise ValueError('actual5436-v2 immutable full11 before required')
    if any(type(v.get(k))is not type(x)or v[k]!=x for k,x in expected.items()):
        raise ValueError('all actual currentA2/full11/native88 projection criteria')


def normalized_text(raw):
    pairs={previous.CURRENT:CURRENT,previous.SOURCE:SOURCE,previous.CURRENT_BOM:CURRENT_BOM,
        previous.candidate_bom():candidate_bom(),previous.BEFORE:BEFORE,
        'PG4860':'PG4980','pg4860':'pg4980','PG4980':'PG5430','pg4980':'pg5430',
        previous.view.SLOT:view.SLOT,previous.TOOLS:TOOLS,previous.SAVE:SAVE,
        previous.ARCHIVE:ARCHIVE,previous.REMOTE:REMOTE,
        'pg4986':'pg5438','Pg4986':'Pg5438','PG4986':'PG5438',
        'pg4988':'pg5440','PG4988':'PG5440','pg4990':'pg5442','PG4990':'PG5442',
        'pg4992':'pg5444','PG4992':'PG5444'}
    pattern='|'.join(re.escape(k)for k in sorted(pairs,key=len,reverse=True))
    def replace(match):
        token=match.group();first,last=match.span()
        if re.fullmatch('[a-f0-9]{40,64}',token)and((first and raw[first-1]in'0123456789abcdefABCDEF')or(last<len(raw)and raw[last]in'0123456789abcdefABCDEF')):
            return token
        return pairs[token]
    return re.sub(pattern,replace,raw)


def role_text(raw):return bind_preserving_payloads(previous.role_text(raw),normalized_text)


@lru_cache(maxsize=1)
def current_tuple():
    current=original.previous.binding(pinned(LATEST,'pg5060_parent_receipt.py'))
    _,_,summary,ended=completed.context()
    if current['boot']!=BOOT.replace('-','')or summary['genuineParentDone']is not True or summary['completionCode']!=10:
        raise ValueError('actual completed A2 normal parent; history only, never permission')
    return current,summary,ended


def native_refs(raw):
    ns={**vars(original),'current_tuple':current_tuple}
    result=types.FunctionType(original.native_refs.__code__,ns)(raw)
    marker="'unitFilesActual': file_entries, 'runtime': runtime}"
    if result.count(marker)!=1:raise ValueError('one full native88 actual capture boundary')
    result=result.replace(marker,"'unitFilesActual': file_entries, 'runtime': runtime, 'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}",1)
    marker="require(not pathlib.Path('/proc/225062').exists())";pid=completed.admission.live()['rootPid']
    if result.count(marker)!=1 or type(pid)is not int or pid<=1:raise ValueError('one actual historical A2 root absence boundary')
    return result.replace(marker,"require(not pathlib.Path('/proc/"+str(pid)+"').exists())",1)


def latest_alias(raw):
    return bind_preserving_payloads(raw,lambda text:text.replace('pg5060','pg5438').replace('PG5060','PG5438'))


def sources(bom=None,before=None):
    qualify();actual=candidate_bom()
    if bom is not None and bom!=actual or before is not None and before!=BEFORE:raise ValueError('fixed A2/296 role only')
    factory=previous.FACTORY
    ns={**vars(factory),'CURRENT':CURRENT,'CURRENT_BOM':CURRENT_BOM,'SOURCE':SOURCE,'BOM':actual,'BEFORE':BEFORE,
        'BOOT':BOOT,'TOOLS':TOOLS,'SAVE':SAVE,'ARCHIVE':ARCHIVE,'REMOTE':REMOTE,'BASE':BASE,'LATEST':LATEST,
        'qualify':qualify,'role_text':role_text,'current_tuple':current_tuple,'native_refs':native_refs,
        'latest_alias':latest_alias,'candidate_bom':candidate_bom}
    raw=inspect.getsource(factory.sources)
    for old,new in(('pg3982','pg5438'),('Pg3982','Pg5438'),('PG3982','PG5438'),('pg3876','pg5060'),('Pg3876','Pg5060'),('PG3876','PG5060')):
        raw=raw.replace(old,new)
    exec(compile(raw,'<all18 A2/296 immutable unused roles>','exec'),ns)
    return ns['sources']()


if __name__=='__main__':raise SystemExit('pure factory; no guest action')
