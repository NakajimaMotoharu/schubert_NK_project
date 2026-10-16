"""Finite code-only publication of qualified RO candidate; completed data is not authority."""
import json
from pyflakes.api import check
from bundle_hash_contract import unbind
import pg3756_hygiene_unused_sources as mapping
import pg3780_hygiene_ro_sources as ro

W=ro.W;CURRENT=ro.CURRENT;CURRENT_BOM=ro.unused.CURRENT_BOM;SOURCE=ro.SOURCE;BOM=ro.BOM;BEFORE=ro.BEFORE;BOOT=ro.unused.BOOT
TOOLS='pg3788-hygiene-publication-tools-v1';SAVE='pg3792-hygiene-publication-v1';CLASS='Pg3788OrdinaryPublication'
BASE=W/'pg3450-current-outbox-publication-tools-v1'


def qualify():
    ro.qualify()
    value=json.loads((W/'pg3786-hygiene-ro-independent-post-v1/manifest.safe.json').read_bytes())
    result=value.get('result',{})
    if value.get('actualExit')!=0 or result.get('actualExit')!=0 or result.get('candidateHostReadonlyVerified')is not True or result.get('candidateSource')!=SOURCE or result.get('currentSource')!=CURRENT or result.get('candidateManifestSha256')!=BOM or result.get('allClientAdvisoryMA0')is not True or result.get('newTenReferencesReturnedNormally')is not True:raise ValueError('same signed unused RO candidate/full current post required')
    return result


def bind(raw):
    raw=mapping.role_text(raw)
    for a,b in [('pg3450-current-outbox-publication-tools-v1',TOOLS),('pg3456-current-outbox-publication-v1',SAVE),('pg3446-current-outbox-ro-completed-v1',ro.SAVE),('pg3450','pg3788'),('Pg3450','Pg3788'),('PG3450','PG3788'),('pg3452','pg3790'),('PG3452','PG3790'),('pg3454','pg3792'),('PG3454','PG3792')]:raw=raw.replace(a,b)
    return raw


def sources(bom=BOM,before=BEFORE):
    qualify()
    if bom!=BOM or before!=BEFORE:raise ValueError('exact signed candidate/current data only')
    names=sorted(n for n in json.loads((BASE/'payload-sha256.json').read_bytes())if n.endswith(('.py','.java')))
    result={bind(n):bind(mapping.pinned(BASE,n))for n in names}
    result['pg3788_native_refs.py']=unbind(mapping.native_refs(result['pg3788_native_refs.py']))
    normal=ro.sources()
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:
        result['pg3788_'+suffix]=normal['pg3780_'+suffix].replace('pg3780','pg3788').replace('PG3780','PG3788')
    result['Pg3788OriginalTupleTest.java']=normal['Pg3780OriginalTupleTest.java'].replace('Pg3780CandidateRo',CLASS).replace('Pg3780','Pg3788').replace('PG3780','PG3788')
    old=result[CLASS+'.java'];start=old.index('  static void verifyOriginalValues(');end=old.index('\n  static void verifyOriginal()',start)
    new=normal['Pg3780CandidateRo.java'];a=new.index('  static void verifyOriginalValues(');b=new.index('\n  static void verifyOriginal()',a)
    result[CLASS+'.java']=old[:start]+new[a:b]+old[end:]
    current,_,ended=mapping.current_tuple()
    # These three files contain positive Root constants, no negative UUID fixtures.
    for name in [CLASS+'.java','Pg3788TransitionTest.java','pg3788_ordinary_publication_contract.py']:
        raw=result[name]
        for a,b in [('0dc63b79-3f9a-450c-b2a6-56f86272d272',current['run']),('323bc9ad-1528-449a-8067-19228ee1e046',current['activation']),('2026-10-14T19:12:28.842213Z',current['cutoff']),('2026-10-15T02:15:14.431931Z',ended)]:raw=raw.replace(a,b)
        result[name]=raw
    if len(result)!=24:raise ValueError('all twenty-four finite publication source roles')
    for name,raw in result.items():
        if name.endswith('.py'):
            context="BUNDLE_HASH='pending-real-bundle'\n"if name=='pg3788_native_refs.py'else ''
            if check(context+raw,'<whole finite publication graph>'):raise ValueError('complete namespace required')
            compile(context+raw,'<finite current4856 candidate7fff publication>','exec')
    return result
