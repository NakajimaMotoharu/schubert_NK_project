"""Distinct unused candidate0ea over fresh current296/full11/native94; no start authority."""
import hashlib
import inspect
import json
import re
import types
from functools import lru_cache
from types import SimpleNamespace
import pg5438_ownership_unused_sources as previous
import pg5496_current_owned_sources as completed
import pg5606_current_full_preservation as capture
from immutable_payload_binding import bind_preserving_payloads
from pg5598_current_signed_candidate import SOURCE,OLD_SOURCE,OLD_BOM

W=capture.W
CURRENT,CURRENT_BOM,CANDIDATE=OLD_SOURCE,OLD_BOM,SOURCE
BEFORE='9c1bdb509883f70f20f73d502553777823ca83fce728505f62dd534986722cb7'
BOM='1aa1fb6300946d086c60f005f6e4253b1ffd0da873ada103dd89c94cac89b173'
BOOT=previous.BOOT
TOOLS='pg5608-current-unused-tools-v1'
SAVE='pg5612-current-unused-placement-v1'
ARCHIVE='pg5612-current-release-v1.tar'
REMOTE='/home/ubuntu/pg5612-current-input-v1'
VIEW_LOCAL=W/capture.SLOT/'manifest.safe.json'
view=SimpleNamespace(SLOT=capture.SLOT,FIELDS=capture.FIELDS,before=capture,W=W)
BASE,pinned=previous.BASE,previous.pinned
LATEST=W/completed.TOOLS
original=previous.original


def candidate_bom():
    path=W/'pg5598-candidate-build-v1.safe.json';raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='d1214e27276ffa7a368c593e36904fb39f48f5dac3d62a0fa54eafebf32491df':raise ValueError('immutable actual host candidate, not inferred signature')
    value=json.loads(raw)
    if not(value['actualExit']==0 and value['candidateSource']==SOURCE and value['priorSource']==CURRENT and value['manifestSha256']==BOM
      and value['signatureVerified']and value['candidateNotDeployed']and not value['formalAccepted']):raise ValueError('distinct current/candidate signed roles')
    return BOM


def production():return SOURCE


def qualify():
    candidate_bom();raw=VIEW_LOCAL.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='cdb5e245a218dab0e7e125e032f55ef227d044ada200dfe2c2f99c293fbb5ed5':raise ValueError('actual fresh before-image manifest only')
    outer=json.loads(raw);v=outer['result']
    expected={'actualExit':0,'productionSource':CURRENT,'BOM':CURRENT_BOM,'privateBeforeSha256':BEFORE,
      'sealedFull11Fields':11,'tables':24,'all24EqualTwice':True,'unitCount':10,'nativePhysicalFiles':94,
      'all92OriginalAndTenCatalogUnionPreserved':True,'allTenRefsReturnedNormally':True,'freshPid1HistoryMatches':True,
      'allOriginalBackupCredentialTreesUnchanged':True,'allClientAdvisoryFlock0':True,'allKernelActor0':True,
      'startsStopsReloadsSqlWrites0':True,'dataOnlyNotRuntimeAuthority':True,'oldNativeAcceptanceImported':False,'formalAccepted':False}
    if type(outer['actualExit'])is not int or outer['actualExit']!=0 or outer['source']!=CURRENT or outer['oldStopReissued']is not False:raise ValueError('genuine new capture, not old stop replay')
    if any(type(v.get(k))is not type(value)or v[k]!=value for k,value in expected.items()):raise ValueError('all fresh full11 conditions, not MainPID-only inference')


def normalized_text(raw):
    pairs={previous.CURRENT:CURRENT,previous.SOURCE:SOURCE,previous.CURRENT_BOM:CURRENT_BOM,previous.candidate_bom():BOM,previous.BEFORE:BEFORE,
      'PG4980':'PG5430','pg4980':'pg5430','PG5430':'PG5598','pg5430':'pg5598',previous.view.SLOT:view.SLOT,
      previous.TOOLS:TOOLS,previous.SAVE:SAVE,previous.ARCHIVE:ARCHIVE,previous.REMOTE:REMOTE,
      'pg5438':'pg5608','Pg5438':'Pg5608','PG5438':'PG5608','pg5440':'pg5610','PG5440':'PG5610',
      'pg5442':'pg5612','PG5442':'PG5612','pg5444':'pg5614','PG5444':'PG5614'}
    pattern='|'.join(re.escape(k)for k in sorted(pairs,key=len,reverse=True))
    def replace(match):
        token=match.group();start,end=match.span()
        if re.fullmatch('[0-9a-f]{40,64}',token)and((start and raw[start-1]in'0123456789abcdefABCDEF')or(end<len(raw)and raw[end]in'0123456789abcdefABCDEF')):return token
        return pairs[token]
    return re.sub(pattern,replace,raw)


def role_text(raw):return bind_preserving_payloads(previous.role_text(raw),normalized_text)


@lru_cache(maxsize=1)
def current_tuple():
    current=original.previous.binding(pinned(LATEST,'pg5496_parent_receipt.py'))
    _,_,summary,ended=completed.context()
    if current['boot']!=BOOT.replace('-','')or summary['genuineParentDone']is not True or summary['completionCode']!=10:raise ValueError('actual closed296 history only, not live/start permission')
    return current,summary,ended


def native_refs(raw):
    ns={**vars(original),'current_tuple':current_tuple}
    result=types.FunctionType(original.native_refs.__code__,ns)(raw)
    marker="'unitFilesActual': file_entries, 'runtime': runtime}"
    if result.count(marker)!=1:raise ValueError('one complete full11/native94 capture boundary')
    result=result.replace(marker,"'unitFilesActual': file_entries, 'runtime': runtime, 'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}",1)
    marker="require(not pathlib.Path('/proc/225062').exists())";pid=completed.admission.live()['rootPid']
    if result.count(marker)!=1 or type(pid)is not int or pid<=1:raise ValueError('one historical currentRoot absence selector')
    return result.replace(marker,"require(not pathlib.Path('/proc/"+str(pid)+"').exists())",1)


def latest_alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg5496','pg5608').replace('PG5496','PG5608'))


def sources(bom=None,before=None):
    qualify();actual=candidate_bom()
    if bom is not None and bom!=actual or before is not None and before!=BEFORE:raise ValueError('fixed296/0ea new roles only')
    factory=previous.previous.FACTORY
    ns={**vars(factory),'CURRENT':CURRENT,'CURRENT_BOM':CURRENT_BOM,'SOURCE':SOURCE,'BOM':actual,'BEFORE':BEFORE,
      'BOOT':BOOT,'TOOLS':TOOLS,'SAVE':SAVE,'ARCHIVE':ARCHIVE,'REMOTE':REMOTE,'BASE':BASE,'LATEST':LATEST,
      'qualify':qualify,'role_text':role_text,'current_tuple':current_tuple,'native_refs':native_refs,'latest_alias':latest_alias,'candidate_bom':candidate_bom}
    raw=inspect.getsource(factory.sources)
    for old,new in(('pg3982','pg5608'),('Pg3982','Pg5608'),('PG3982','PG5608'),('pg3876','pg5496'),('Pg3876','Pg5496'),('PG3876','PG5496')):raw=raw.replace(old,new)
    exec(compile(raw,'<all18 distinct296/0ea unused roles>','exec'),ns)
    return ns['sources']()


if __name__=='__main__':raise SystemExit('pure source factory; no guest operation')
