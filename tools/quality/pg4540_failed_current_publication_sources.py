"""SSC296 finite publication: failed old data and new normal authority never conflated."""
import ast
import json
from pyflakes.api import check
from immutable_payload_binding import bind_preserving_payloads
import pg4002_literal_invariant_publication_sources as historical
import pg4522_failed_current_ro_sources as ro

W,CURRENT,SOURCE,BOM,BEFORE,BOOT=(ro.W,ro.CURRENT,ro.SOURCE,ro.BOM,ro.BEFORE,ro.unused.BOOT)
CURRENT_BOM=ro.unused.CURRENT_BOM
TOOLS='pg4540-failed-current-publication-tools-v2';SAVE='pg4544-failed-current-publication-v2';CLASS='Pg4540OrdinaryPublication'
BASE=historical.BASE


def qualify_result(value):
    result=ro.qualify_result(value)
    if result.get('candidateHostReadonlyVerified')is not True:raise ValueError('same candidate actual PID1 RO post first')
    return result


def qualify():
    ro.qualify();return qualify_result(json.loads((W/'pg4534-failed-current-ro-post-v1/manifest.safe.json').read_bytes()))


def bind(raw):
    raw=ro.unused.previous.previous.role_text(raw)
    return raw.replace(historical.TOOLS,TOOLS).replace(historical.SAVE,SAVE).replace(historical.ro.TOOLS,ro.TOOLS).replace(historical.ro.SAVE,ro.SAVE).replace('pg4002','pg4540').replace('Pg4002','Pg4540').replace('PG4002','PG4540').replace('pg4004','pg4542').replace('PG4004','PG4542').replace('pg4006','pg4544').replace('PG4006','PG4544')


def alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg4522','pg4540').replace('Pg4522','Pg4540').replace('PG4522','PG4540'))


def build_sources():
    values={bind(name):bind(raw)for name,raw in historical.sources().items()}
    normal=ro.sources();once=ro.unused.previous.previous.once
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:values['pg4540_'+suffix]=alias(normal['pg4522_'+suffix])
    values['Pg4540OriginalTupleTest.java']=alias(normal['Pg4522OriginalTupleTest.java'].replace('Pg4522CandidateRo',CLASS))
    name=CLASS+'.java';old=values[name];new=normal['Pg4522CandidateRo.java']
    start=old.index('  static void verifyOriginalValues(');end=old.index('\n  static void verifyOriginal()',start)
    a=new.index('  static void verifyOriginalValues(');b=new.index('\n  static void verifyOriginal()',a)
    raw=old[:start]+new[a:b]+old[end:]
    raw=raw.replace('COMPLETED_ORIGINAL','FAILED_PARENT_DATA')
    raw=once(raw,'genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true','genuineParentNormalWarningOriginal=false\\ncurrentManagerGc=false\\nfailedParent143DataOnly=true')
    raw=once(raw,'startsStopsReloadsEpochWrites0=true\\noldUnknownNormalized=false','startsStopsReloadsBusinessWrites0=true\\ncanonicalInvalidEpochWritten=true\\noldUnknownNormalized=false')
    values[name]=raw.replace('startsStopsReloadsEpochWrites0=true databaseUpdates0=true','startsStopsReloadsBusinessWrites0=true canonicalInvalidEpochWritten=true databaseUpdates0=true')
    name='Pg4540TransitionTest.java';raw=values[name]
    raw=once(raw,'invalidExpected=null;Pg4540OrdinaryPublication.transitionOriginal(e(StartupPermitRecords.State.ISSUED,BOOT,FRESH,ACTIVATION),done);checks++;','invalidExpected=null;Pg4540OrdinaryPublication.transitionOriginal(e(StartupPermitRecords.State.INVALID,BOOT,FRESH,ACTIVATION),done);checks++;')
    values[name]=once(raw,'  reject(e(StartupPermitRecords.State.INVALID,BOOT,FRESH,ACTIVATION),done);','  reject(e(StartupPermitRecords.State.ISSUED,BOOT,FRESH,ACTIVATION),done);')
    name='pg4540_native_refs.py';raw=values[name].replace('qualify_warning_parent','qualify_failed_parent')
    for old,new in [('from pg4540_parent_receipt import completed','from pg4540_parent_receipt import failed_completed'),("completed(rows, done)['endMonotonicUs']","failed_completed(rows, done)['endMonotonicUs']"),
      ("INV = '898f87b2f2c4406fb75011eb377dfb77'","INV = 'bbcdb69957764d489a9c757b441542fd'"),('START = 115525825161','START = 149622262076'),('END = 117228974666','END = 151422334917'),("not pathlib.Path('/proc/225062').exists()","not pathlib.Path('/proc/795724').exists()"),
      ("UNITS, FIELDS = (sealed['UNITS'], sealed['FIELDS'])","UNITS, FIELDS = (sealed['UNITS'], set("+repr(ro.PARENT_FIELDS)+'))')]:raw=once(raw,old,new)
    values[name]=raw
    if len(values)!=24:raise ValueError('all24 finite publication roles')
    for name,raw in values.items():
        if name.endswith('.py'):
            context="BUNDLE_HASH='pending-real-bundle'\n"if name=='pg4540_native_refs.py'else''
            if check(context+raw,'<full failed-data publication namespace>'):raise ValueError('all emitted static0')
            ast.parse(context+raw)
    return values


def sources(bom=BOM,before=BEFORE):
    qualify()
    if bom!=BOM or before!=BEFORE:raise ValueError('fixed old data/new signed source')
    return build_sources()
