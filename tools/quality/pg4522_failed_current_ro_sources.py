"""SSC296 current failed-data plus signed unused964e candidate RO, no old authority."""
import ast
import json
from pyflakes.api import check
from immutable_payload_binding import bind_preserving_payloads
import pg3994_literal_invariant_ro_sources as historical
import pg4498_set_typed_unused_sources as unused
from pg4438_failed_current_canonical_view import PARENT_FIELDS

W,CURRENT,SOURCE,BOM,BEFORE=(unused.W,unused.CURRENT,unused.SOURCE,unused.BOM,unused.BEFORE)
TOOLS='pg4522-failed-current-ro-tools-v1';SAVE='pg4526-failed-current-ro-completed-v1';CLASS='Pg4522CandidateRo'
BASE=historical.BASE


def qualify_result(value):
    def require(v):
        if v is not True:raise ValueError('genuine newsource unused post required')
    require(type(value)is dict and type(value.get('actualExit'))is int and value['actualExit']==0)
    require(value.get('formalAccepted')is False)
    require(value.get('currentSource')==CURRENT and value.get('candidateSource')==SOURCE and CURRENT!=SOURCE)
    r=value.get('result');require(type(r)is dict and type(r.get('actualExit'))is int and r['actualExit']==0)
    require(r.get('source')==r.get('currentSource')==CURRENT and r.get('candidateSource')==SOURCE and r.get('candidateManifestSha256')==BOM
      and r.get('BOM')==unused.CURRENT_BOM and r.get('oldParentNormal')is False and r.get('candidateNativeCredit')is False)
    require(r.get('formalAccepted')is False and type(r.get('signalStartStopReloadDbWrites'))is int and r['signalStartStopReloadDbWrites']==0)
    flags=['newMARDDBTenRefNormalClose','all24OriginalBackupNativeUnitConfigUnchanged','parent143StillFailed','candidateUnusedOnly','candidate187SignatureVerified',
        'candidatePermissionsVerified','configuration32EveryFieldUnchanged','all24TablesEqualTwice','allClientAdvisoryMA0','newTenReferencesReturnedNormally','native58Preserved','runtimeStartupAndApprovalEpochUnchanged']
    require(all(r.get(k)is True for k in flags));require(r.get('beforeSha256')==r.get('afterSha256')=='148a8d8a3a3284dbf4a72833ca808ca8a07cee84a85b5562f07356006ac91148')
    return r


def qualify():
    unused.qualify();return qualify_result(json.loads((W/'pg4520-failed-current-unused-post-v1/manifest.safe.json').read_bytes()))


def bind(raw):
    raw=unused.previous.previous.role_text(raw)
    return raw.replace(historical.TOOLS,TOOLS).replace(historical.SAVE,SAVE).replace('pg3994','pg4522').replace('Pg3994','Pg4522').replace('PG3994','PG4522').replace('pg3996','pg4524').replace('PG3996','PG4524').replace('pg3998','pg4526').replace('PG3998','PG4526')


def alias(raw):
    return bind_preserving_payloads(raw,lambda text:text.replace('pg4444','pg4522').replace('Pg4444','Pg4522').replace('PG4444','PG4522'))


def build_sources():
    # Historical source templates only. Their old success/permit/native results
    # are never used by qualify_result or as current runtime authority.
    values={bind(name):bind(raw)for name,raw in historical.sources().items()}
    normal=unused.sources();once=unused.previous.previous.once
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:values['pg4522_'+suffix]=alias(normal['pg4444_'+suffix])
    values['Pg4522OriginalTupleTest.java']=alias(normal['Pg4444OriginalTupleTest.java'].replace('Pg4444UnusedStage','Pg4522CandidateRo'))
    name='Pg4522CandidateRo.java';old=values[name];new=normal['Pg4444UnusedStage.java']
    start=old.index('  static void verifyOriginalValues(');end=old.index('\n  static void verifyOriginal()',start)
    a=new.index('  static void verifyOriginalValues(');b=new.index('\n  static void verifyOriginal()',a)
    raw=old[:start]+new[a:b]+old[end:]
    raw=raw.replace('COMPLETED_ORIGINAL','FAILED_PARENT_DATA')
    raw=once(raw,'genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true','genuineParentNormalWarningOriginal=false\\ncurrentManagerGc=false\\nfailedParent143DataOnly=true')
    values[name]=raw
    name='pg4522_native_refs.py';raw=values[name]
    raw=raw.replace('qualify_warning_parent','qualify_failed_parent')
    raw=once(raw,'from pg4522_parent_receipt import completed','from pg4522_parent_receipt import failed_completed')
    raw=once(raw,"completed(rows, done)['endMonotonicUs']","failed_completed(rows, done)['endMonotonicUs']")
    for old,new in [("INV = '898f87b2f2c4406fb75011eb377dfb77'","INV = 'bbcdb69957764d489a9c757b441542fd'"),('START = 115525825161','START = 149622262076'),('END = 117228974666','END = 151422334917'),("not pathlib.Path('/proc/225062').exists()","not pathlib.Path('/proc/795724').exists()"),
      ("UNITS, FIELDS = (sealed['UNITS'], sealed['FIELDS'])","UNITS, FIELDS = (sealed['UNITS'], set("+repr(PARENT_FIELDS)+'))')]:raw=once(raw,old,new)
    values[name]=raw
    if len(values)!=18:raise ValueError('complete eighteen RO roles')
    for name,raw in values.items():
        if name.endswith('.py'):
            context="BUNDLE_HASH='pending-real-bundle'\n"if name=='pg4522_native_refs.py'else''
            if check(context+raw,'<complete failed-data RO source>'):raise ValueError('all emitted static0')
            ast.parse(context+raw)
    return values


def sources(bom=BOM,before=BEFORE):
    qualify()
    if bom!=BOM or before!=BEFORE:raise ValueError('fixed failed-current/candidate roles')
    return build_sources()
