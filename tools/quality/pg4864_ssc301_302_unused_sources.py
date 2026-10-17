"""Exact stopped825e data and distinct signed04bb unused role; no live authority."""
import inspect
import json
import re
from functools import lru_cache
import pg4706_ssc299_unused_sources as previous
import pg4772_new_current_owned_sources as completed
import pg4862_current_preservation_readonly as view
from immutable_payload_binding import bind_preserving_payloads
from pg4844_ssc301_302_full import SOURCE, W

CURRENT, CURRENT_BOM, BOOT = completed.SOURCE, completed.BOM, previous.BOOT
BEFORE = '79805587c817ef40ce0df1d2d1eb0e2e36e27d6bb8fb1e32a69c564ae9903b46'
TOOLS = 'pg4864-ssc301-302-unused-tools-v1'
SAVE = 'pg4868-ssc301-302-unused-placement-v1'
ARCHIVE = 'pg4868-ssc301-302-release-v1.tar'
REMOTE = '/home/ubuntu/pg4868-ssc301-302-input-v1'
VIEW_LOCAL = W / view.SLOT / 'manifest.safe.json'
BASE, pinned = previous.BASE, previous.pinned
LATEST = W / completed.TOOLS


def candidate_bom():
    value = json.loads((W/'pg4860-candidate-build-v1.safe.json').read_bytes())
    wanted = {'actualExit':0,'candidateSource':SOURCE,'priorSource':CURRENT,'signatureVerified':True,
              'candidateNotDeployed':True,'formalAccepted':False,'allSixFormatBeforeAnyPt':True,
              'manifestSha256':'08300d492e9eb5ba6e31eb646c21e51fc3eb4d30680e205c2adcd35c92d298b2'}
    if any(type(value.get(k)) is not type(v) or value[k] != v for k,v in wanted.items()):
        raise ValueError('actual new signed candidate, not current/format history')
    return value['manifestSha256']


def production(): return SOURCE


def qualify():
    outer = json.loads(VIEW_LOCAL.read_bytes()); value = outer['result']; candidate_bom()
    wanted = {'actualExit':0,'productionSource':CURRENT,'freshCurrentPreservation':True,
              'whole24Full32Signed187AndResourcesUnchanged':True,'allResources0':True,
              'normalNewReferences':True,'capturedNormal20VerifiedBeforeCurrent':True,
              'bootstrapCredentialsAbsent':True,'currentCredentialsRetired':True,
              'nativePhysicalFiles':72,'privateBeforeSha256':BEFORE,'sealedFull11Fields':11,
              'dataOnlyNotRuntimeAuthority':True,'nativeCandidateCredit':False,
              'currentOriginalClosedAndNoIntent':True,'runtimeConfigFilesToRetire':0}
    if type(outer['actualExit']) is not int or outer['actualExit'] != 0 or outer['source'] != CURRENT:
        raise ValueError('fresh completed current data first')
    if any(type(value.get(k)) is not type(v) or value[k] != v for k,v in wanted.items()):
        raise ValueError('all exact current full/Bootstrap20 data criteria')


def normalized_text(raw):
    pairs = {previous.CURRENT:CURRENT,previous.SOURCE:SOURCE,previous.CURRENT_BOM:CURRENT_BOM,
             previous.candidate_bom():candidate_bom(),previous.BEFORE:BEFORE,
             'PG4702':'PG4860','pg4702':'pg4860','PG4432':'PG4702','pg4432':'pg4702',
             'pg4704-current-preservation-readonly-v1':view.SLOT,
             previous.TOOLS:TOOLS,previous.SAVE:SAVE,previous.ARCHIVE:ARCHIVE,previous.REMOTE:REMOTE,
             'pg4706':'pg4864','Pg4706':'Pg4864','PG4706':'PG4864',
             'pg4708':'pg4866','PG4708':'PG4866','pg4710':'pg4868','PG4710':'PG4868',
             'pg4712':'pg4870','PG4712':'PG4870'}
    pattern = '|'.join(re.escape(k) for k in sorted(pairs,key=len,reverse=True))
    def replace(match):
        token=match.group();first,last=match.span()
        if re.fullmatch('[a-f0-9]{40,64}',token) and ((first and raw[first-1] in '0123456789abcdefABCDEF') or (last<len(raw) and raw[last] in '0123456789abcdefABCDEF')): return token
        return pairs[token]
    return re.sub(pattern,replace,raw)


def role_text(raw): return normalized_text(previous.role_text(raw))


@lru_cache(maxsize=1)
def current_tuple():
    raw=inspect.getsource(previous.current_tuple.__wrapped__).replace('pg4652_parent_receipt.py','pg4772_parent_receipt.py')
    ns={**vars(previous),'LATEST':LATEST,'completed':completed,'BOOT':BOOT}
    exec(compile(raw,'<actual current825e completed tuple data>','exec'),ns)
    return ns['current_tuple']()


def native_refs(raw):
    ns={**vars(previous.previous.previous),'current_tuple':current_tuple}
    exec(compile(inspect.getsource(previous.previous.previous.native_refs),'<actual normal825e native reference data>','exec'),ns)
    result=ns['native_refs'](raw)
    # The fresh current image includes all72 native entries. Capture the actual
    # same tree under the already-owned scopes; never drop it to fit legacy10.
    marker="'unitFilesActual': file_entries, 'runtime': runtime}"
    if result.count(marker)!=1:raise ValueError('one actual capture_data return')
    result=result.replace(marker,"'unitFilesActual': file_entries, 'runtime': runtime, 'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}",1)
    marker="require(not pathlib.Path('/proc/225062').exists())"
    root_pid=completed.admission.live()['rootPid']
    if result.count(marker)!=1 or type(root_pid)is not int or root_pid!=860231:
        raise ValueError('one actual825e closed Root generation, not old PID authority')
    result=result.replace(marker,"require(not pathlib.Path('/proc/"+str(root_pid)+"').exists())",1)
    return result


def latest_alias(raw):
    return bind_preserving_payloads(raw,lambda value:value.replace('pg4772','pg4864').replace('PG4772','PG4864'))


def sources(bom=None,before=None):
    qualify(); actual=candidate_bom()
    if bom is not None and bom != actual or before is not None and before != BEFORE:
        raise ValueError('one fixed current825e/candidate04bb data role')
    ns={**vars(previous.previous),'CURRENT':CURRENT,'CURRENT_BOM':CURRENT_BOM,'SOURCE':SOURCE,
        'BOM':actual,'BEFORE':BEFORE,'BOOT':BOOT,'TOOLS':TOOLS,'SAVE':SAVE,'ARCHIVE':ARCHIVE,
        'REMOTE':REMOTE,'BASE':BASE,'LATEST':LATEST,'qualify':qualify,'role_text':role_text,
        'current_tuple':current_tuple,'native_refs':native_refs,'latest_alias':latest_alias,'candidate_bom':candidate_bom}
    raw=inspect.getsource(previous.previous.sources)
    for old,new in [('pg3982','pg4864'),('Pg3982','Pg4864'),('PG3982','PG4864'),('pg3876','pg4772'),('Pg3876','Pg4772'),('PG3876','PG4772')]: raw=raw.replace(old,new)
    exec(compile(raw,'<complete distinct unused eighteen roles>','exec'),ns)
    return ns['sources']()


if __name__ == '__main__': raise SystemExit('pure factory; no guest action')
