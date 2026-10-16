"""Pinned RO template, current completed data and new candidate are separate roles."""
import json
from pyflakes.api import check
from bundle_hash_contract import unbind
import pg3756_hygiene_unused_sources as mapping
import pg3766_hygiene_unused_sources_v2 as unused

W=unused.W;CURRENT=unused.CURRENT;SOURCE=unused.SOURCE;BOM=unused.BOM;BEFORE=unused.BEFORE
TOOLS='pg3780-hygiene-ro-tools-v1';SAVE='pg3784-hygiene-ro-completed-v1';CLASS='Pg3780CandidateRo'
BASE=W/'pg3442-current-outbox-ro-tools-v1'


def qualify():
    unused.qualify()
    proof=json.loads((W/'pg3778-hygiene-unused-held-post-v1/manifest.safe.json').read_bytes())
    result=proof.get('result',{})
    required=['candidateUnusedOnly','candidate187SignatureVerified','current187SignatureVerified',
              'configuration32EveryFieldUnchanged','all24TablesEqualTwice','allClientAdvisoryMA0',
              'newTenReferencesReturnedNormally','native34Preserved','runtimeStartupAndApprovalEpochUnchanged']
    if proof.get('actualExit')!=0 or result.get('actualExit')!=0 or result.get('candidateSource')!=SOURCE or result.get('currentSource')!=CURRENT or result.get('candidateManifestSha256')!=BOM or any(result.get(k)is not True for k in required):
        raise ValueError('genuine unused full post and separate current/candidate required')
    return result


def bind(raw):
    raw=mapping.role_text(raw)
    for a,b in [('pg3442-current-outbox-ro-tools-v1',TOOLS),('pg3446-current-outbox-ro-completed-v1',SAVE),('pg3442','pg3780'),('Pg3442','Pg3780'),('PG3442','PG3780'),('pg3444','pg3782'),('PG3444','PG3782'),('pg3446','pg3784'),('PG3446','PG3784')]:raw=raw.replace(a,b)
    return raw


def sources(bom=BOM,before=BEFORE):
    qualify()
    if bom!=BOM or before!=BEFORE:raise ValueError('fixed current/candidate data required')
    names=sorted(n for n in json.loads((BASE/'payload-sha256.json').read_bytes())if n.endswith(('.py','.java')))
    result={bind(n):bind(mapping.pinned(BASE,n))for n in names}
    result['pg3780_native_refs.py']=unbind(mapping.native_refs(result['pg3780_native_refs.py']))
    normal=unused.sources()
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:
        result['pg3780_'+suffix]=normal['pg3766_'+suffix].replace('pg3766','pg3780').replace('PG3766','PG3780')
    result['Pg3780OriginalTupleTest.java']=normal['Pg3766OriginalTupleTest.java'].replace('Pg3766UnusedStage','Pg3780CandidateRo').replace('Pg3766','Pg3780').replace('PG3766','PG3780')
    old=result['Pg3780CandidateRo.java'];start=old.index('  static void verifyOriginalValues(');end=old.index('\n  static void verifyOriginal()',start)
    new=normal['Pg3766UnusedStage.java'];a=new.index('  static void verifyOriginalValues(');b=new.index('\n  static void verifyOriginal()',a)
    result['Pg3780CandidateRo.java']=old[:start]+new[a:b]+old[end:]
    if len(result)!=18:raise ValueError('all eighteen RO sources required')
    for name,raw in result.items():
        if name.endswith('.py'):
            context="BUNDLE_HASH='pending-real-bundle'\n"if name=='pg3780_native_refs.py'else ''
            if check(context+raw,'<new whole RO source>'):raise ValueError('whole namespace required')
            compile(context+raw,'<new RO candidate source>','exec')
    return result
