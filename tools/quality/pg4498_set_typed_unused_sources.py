"""BUG1363 new-only v5 caller matches the sealed full-field set contract."""
import ast
import hashlib
import pg4454_inspectable_failed_unused_sources as previous
from pg4438_failed_current_canonical_view import PARENT_FIELDS

W,CURRENT,CURRENT_BOM,SOURCE,BOM,BEFORE,BOOT=(previous.W,previous.CURRENT,previous.CURRENT_BOM,previous.SOURCE,previous.BOM,previous.BEFORE,previous.BOOT)
TOOLS='pg4444-failed-current-unused-tools-v5';SAVE='pg4448-failed-current-unused-placement-v5'
ARCHIVE='pg4448-shared-manager-release-v5.tar';REMOTE='/home/ubuntu/pg4448-shared-manager-input-v5';PROOF_SAVE=SAVE+'-inspect'
qualify,candidate_bom,production,pinned=(previous.qualify,previous.candidate_bom,previous.production,previous.pinned)


def role_text(raw):
    return raw.replace(previous.TOOLS,TOOLS).replace(previous.SAVE,SAVE).replace(previous.ARCHIVE,ARCHIVE).replace(previous.REMOTE,REMOTE)


def sources(bom=None,before=None):
    values={name:role_text(raw)for name,raw in previous.sources(bom,before).items()}
    name='pg4444_native_refs.py'
    old="UNITS, FIELDS = (sealed['UNITS'], "+repr(PARENT_FIELDS)+')'
    values[name]=previous.previous.once(values[name],old,"UNITS, FIELDS = (sealed['UNITS'], set("+repr(PARENT_FIELDS)+'))')
    return values


def actual_show():
    # This is the exact deployed sealed source used by the caller's pinned
    # AST extraction, not a reimplementation of show or an invented oracle.
    encoded=(W/'pg4504-post-retainer-full-read-v1/sealed-reference.private.py').read_bytes()
    if hashlib.sha256(encoded).hexdigest()!='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7':raise ValueError('exact deployed sealed source required')
    raw=encoded.decode();candidates=[ast.get_source_segment(raw,n)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='show']
    if len(candidates)!=1:raise ValueError('one actual sealed show definition')
    return candidates[0]
