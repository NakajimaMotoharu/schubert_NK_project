"""Check exact source-closed oracle applicability and negative boundaries, no production execution."""
from pathlib import Path
import copy,hashlib,json
import pgpt_closed_host_profile as p
import pgpt_protocol_public_oracle as q
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';c=json.loads((b/'input/4313_named_record_collection_profile_v3.json').read_text());checks=[]
p.validate_syntax(c);q.checked(c);checks.append('exact_current_module_and_old_oracle_hash_accepted')
original=(r/q.HELPER).read_text();text=q.reviewed_text(c,q.HELPER,original);assert 'Class.forName' not in text and text.count('REVIEWED_PUBLIC_SCALAR_LOOKUP')==4;checks.append('only_four_exact_scalar_anchors')
assert q.reviewed_text(c,'another.java',original)==original;checks.append('other_source_not_masked')
none=copy.deepcopy(c);none.pop('reviewedProtocolPublicOracle');assert q.reviewed_text(none,q.HELPER,original)==original;checks.append('missing_explicit_capability_not_masked')
for label,mutator in [('wrong_test_count',lambda x:x.update(expectedTests=139)),('missing_main',lambda x:x['mainSources'].pop()),('extra_sdk',lambda x:x['sdkJars'].append('unreviewed.jar')),('wrong_helper_count',lambda x:next(t for t in x['testSources'] if t['path']==q.HELPER).update(tests=1)),('unbound_proof',lambda x:x['reviewedProtocolPublicOracle'].update(closureProof=dict(path='evidence/no.json',sha256='0'*64))),('missing_scalar_class',lambda x:x['physicalClasses'].remove('dev/codex/schubert/nk/protocol/layout/semantic/UserId.class'))]:
 candidate=copy.deepcopy(c);mutator(candidate)
 try:q.checked(candidate)
 except (ValueError,AssertionError):checks.append(label+'_rejected')
 else:raise AssertionError(label)
# The same generic input validation still rejects the original unsupported profile, before run.
try:p.checked_inputs(none)
except ValueError as e:assert str(e)=='outside closed ordinary host scope';checks.append('no_flag_still_rejects_unreviewed_ClassForName')
else:raise AssertionError('unreviewed lookup accepted')
p.checked_inputs(c);checks.append('all_source_resource_owner_proof_inputs_checked')
stale=json.loads((b/'input/4284_ssc444_protocol_profile_v3.json').read_text())
try:q.checked(stale)
except ValueError as e:assert str(e)=='whole helper immutable against current closure';checks.append('old140_helper_proof_not_transferred_to_extended_source')
else:raise AssertionError('stale oracle source accepted')
assert original.count(q.COLLECTION_BLOCK)==1 and hashlib.sha256(original.replace(q.COLLECTION_BLOCK,'',1).encode()).hexdigest()==q.HELPER_SHA;checks.append('all_original_oracle_bytes_inverse_exact')
o=b/'evidence/PG36181-named-record-legacy-caller-selftest-v3';o.mkdir();v=dict(actualExit=0,toolChecks=len(checks),checks=checks,sourceToolSha256=hashlib.sha256((r/'tools/quality/pgpt_protocol_public_oracle.py').read_bytes()).hexdigest(),profileToolSha256=hashlib.sha256((r/'tools/quality/pgpt_closed_host_profile.py').read_bytes()).hexdigest(),heldOperations=0,applicationTestsExecuted=0);(o/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolChecks=len(checks),applicationTestsExecuted=0)))
