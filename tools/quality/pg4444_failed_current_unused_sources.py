"""SSC296 exact failed-current data admission; no normal parent authority."""
import ast
import json
import re
from pyflakes.api import check
import pg3982_literal_invariant_unused_sources as previous
import pg4360_pool_bound_partial_sources as frozen
from immutable_payload_binding import bind_preserving_payloads
from pg4438_failed_current_canonical_view import PARENT_FIELDS
from pg4432_shared_manager_signed_candidate import SOURCE, OLD_SOURCE as CURRENT, OLD_BOM as CURRENT_BOM, W

BOM = '93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de'
BEFORE = '66ee6f865210b07ae18e503f21e19abec54c514523bc5ac44cdc736536336e17'
BOOT = '79a3260a-e16d-42bf-942a-b914ed144c28'
TOOLS = 'pg4444-failed-current-unused-tools-v1'; SAVE = 'pg4448-failed-current-unused-placement-v1'
ARCHIVE = 'pg4448-shared-manager-release-v1.tar'; REMOTE = '/home/ubuntu/pg4448-shared-manager-input-v1'
BASE = W / previous.TOOLS
CURRENT_RUN = 'b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1'
CURRENT_ACT = '8314450e-0dd5-4986-875c-81f73e1b50b2'
CURRENT_CUT = '2026-10-16T11:32:53.943173Z'; CURRENT_DONE = '2026-10-16T12:02:16.207621Z'


def require(value, why='exact failed-current data role refused'):
    if not value: raise ValueError(why)


def proof():
    outer = json.loads((W / 'pg4442-failed-current-view-qualified-v1/manifest.safe.json').read_bytes())
    value = outer['result']
    require(outer['actualExit'] == 0 and value['dataViewAccepted'] is True and value['source'] == CURRENT
            and value['BOM'] == CURRENT_BOM and value['canonicalBefore10Sha256'] == BEFORE
            and value['allElevenValuesIdentical'] is True and value['allRawJournalFieldsCursorsAndEventOrderIdentical'] is True
            and value['oldParentNormal'] is False and value['normalReceiptIssued'] is False
            and value['runtimeAuthorityIssued'] is False and value['nativeFiles'] == 58 and value['startupFiles'] == 37)
    return value


def candidate_bom():
    candidate = json.loads((W / 'pg4432-candidate-build-v1.safe.json').read_bytes())
    require(candidate['actualExit'] == 0 and candidate['candidateSource'] == SOURCE and candidate['manifestSha256'] == BOM
            and candidate['signatureVerified'] is True and candidate['candidateNotDeployed'] is True)
    return BOM


def qualify():
    proof(); candidate_bom()


def production(): return SOURCE


def pinned(folder, name):
    return previous.pinned(folder, name)


def role_text(raw):
    pairs = {previous.CURRENT: CURRENT, previous.SOURCE: SOURCE, previous.CURRENT_BOM: CURRENT_BOM, previous.BOM: BOM,
        previous.BEFORE: BEFORE, 'PG3748': 'PG3976', 'pg3748': 'pg3976', 'PG3976': 'PG4432', 'pg3976': 'pg4432',
        previous.TOOLS: TOOLS, previous.SAVE: SAVE, previous.ARCHIVE: ARCHIVE, previous.REMOTE: REMOTE,
        'pg3980-current-7fff-before-view-v1/before.private.json': 'pg4440-failed-full-image-diagnosis-v1/canonical-before10.private.json',
        'pg3982': 'pg4444', 'Pg3982': 'Pg4444', 'PG3982': 'PG4444', 'pg3984': 'pg4446', 'PG3984': 'PG4446',
        'pg3986': 'pg4448', 'PG3986': 'PG4448', 'pg3988': 'pg4450', 'PG3988': 'PG4450',
        'f29290f8-69ed-49fe-9f2f-33b4efdea422': CURRENT_RUN, 'ae1e0e86-2e2f-4e88-96cb-dcc522546a99': CURRENT_ACT,
        '2026-10-16T00:42:20.585755Z': CURRENT_CUT, '2026-10-16T02:32:19.863522Z': CURRENT_DONE}
    pattern = '|'.join(re.escape(key) for key in sorted(pairs, key=len, reverse=True))
    return bind_preserving_payloads(raw, lambda text: re.sub(pattern, lambda match: pairs[match.group()], text))


def parent_source():
    raw = frozen.files()['post.py']; tree = ast.parse(raw)
    nodes = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'PARENT_SOURCE' for x in n.targets)]
    require(len(nodes) == 1)
    source = ast.literal_eval(nodes[0].value)
    facts = proof(); expected = facts['parentFields']
    # All19 live fields are checked separately; classifier then verifies the
    # original typed13, complete failed PID1 tuple and original .done bytes.
    adapter = '''
BINDING=CURRENT_BINDING
EXPECTED_PARENT=EXPECTED_LITERAL
JOURNAL_KEYS=['MESSAGE_ID','UNIT','INVOCATION_ID','JOB_ID','JOB_TYPE','JOB_RESULT','__MONOTONIC_TIMESTAMP','_PID','_UID','_BOOT_ID']
def qualify_failed_parent(fields,configuration=False):
    expected=dict(EXPECTED_PARENT)
    if configuration:expected['SuccessExitStatus']='10'
    require(type(fields)is dict and fields==expected)
    return {'currentManagerGc':False,'normalUnit0or10':False,'stopAuthority':False,'failedParent143Confirmed':True}
def failed_completed(rows,done):
    reduced=[{k:r[k]for k in JOURNAL_KEYS if k in r}for r in rows]
    require(hashlib.sha256(done).hexdigest()=='654073a05ac1101060b235c8dc1e058efb94f0884e4eb87613b7f182b199644a')
    result=classify(SOURCE,BOM,BOOT,EXPECTED_PARENT,reduced,done)
    return {**result,'endMonotonicUs':int(EXPECTED_PARENT['ExecMainExitTimestampMonotonic']),'genuineParentDone':False,'oldParentNormal':False}
'''.replace('EXPECTED_LITERAL', repr(expected))
    return source + '\n' + adapter


def once(raw, old, new):
    require(raw.count(old) == 1, 'one exact source boundary: ' + old[:90])
    return raw.replace(old, new, 1)


def sources(bom=None, before=None):
    qualify(); require(bom is None or bom == BOM); require(before is None or before == BEFORE)
    values = {role_text(name): role_text(raw) for name, raw in previous.sources().items()}
    require(len(values) == 18)
    values['pg4444_parent_receipt.py'] = parent_source()
    values['pg4444_warning_parent_projection.py'] = 'from pg4444_parent_receipt import qualify_failed_parent\n__all__=["qualify_failed_parent"]\n'
    name = 'pg4444_native_refs.py'; raw = values[name]
    raw = raw.replace('qualify_warning_parent', 'qualify_failed_parent')
    raw = once(raw, 'from pg4444_parent_receipt import completed', 'from pg4444_parent_receipt import failed_completed')
    raw = once(raw, "completed(rows, done)['endMonotonicUs']", "failed_completed(rows, done)['endMonotonicUs']")
    raw = once(raw, "INV = '898f87b2f2c4406fb75011eb377dfb77'", "INV = 'bbcdb69957764d489a9c757b441542fd'")
    raw = once(raw, 'START = 115525825161', 'START = 149622262076')
    raw = once(raw, 'END = 117228974666', 'END = 151422334917')
    raw = once(raw, "not pathlib.Path('/proc/225062').exists()", "not pathlib.Path('/proc/795724').exists()")
    raw = once(raw, "UNITS, FIELDS = (sealed['UNITS'], sealed['FIELDS'])", "UNITS, FIELDS = (sealed['UNITS'], " + repr(PARENT_FIELDS) + ')')
    values[name] = raw
    name = 'Pg4444UnusedStage.java'; raw = values[name]
    raw = once(raw, 'epoch.state()==StartupPermitRecords.State.ISSUED', 'epoch.state()==StartupPermitRecords.State.INVALID && epoch.permitDigest().isEmpty()')
    raw = raw.replace('COMPLETED_ORIGINAL', 'FAILED_PARENT_DATA')
    raw = once(raw, 'genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true', 'genuineParentNormalWarningOriginal=false\\ncurrentManagerGc=false\\nfailedParent143DataOnly=true')
    values[name] = raw
    name = 'Pg4444OriginalTupleTest.java'; raw = values[name]
    raw = once(raw, 'rejected(epoch(StartupPermitRecords.State.INVALID,BOOT,activation),d)', 'REJECT_ORIGINAL_BAD_STATE')
    raw = raw.replace('epoch(StartupPermitRecords.State.ISSUED,', 'epoch(StartupPermitRecords.State.INVALID,')
    raw = raw.replace('REJECT_ORIGINAL_BAD_STATE', 'rejected(epoch(StartupPermitRecords.State.ISSUED,BOOT,activation),d)')
    values[name] = raw
    for name, raw in values.items():
        if name.endswith('.py'):
            header = "BUNDLE_HASH='fixed-before-transfer'\n" if name in ['pg4444_native_refs.py','pg4444_input_preflight.py'] else ''
            require(check(header + raw, '<new failed-current complete role>') == 0, name + ': whole namespace static0')
            compile(header + raw, name, 'exec')
    return values


if __name__ == '__main__':
    raise SystemExit('pure factory only; design/proof gates before any VM mutation')
