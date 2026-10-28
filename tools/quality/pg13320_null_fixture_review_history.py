"""Pinned four-purpose history only; later source edits cannot rewrite historical review evidence."""
import g07_host_class_provenance_inputs as data
from pg13312_web_business_trace_v2 import state_after as previous_state
def state_after():
    path = data.BASE/'PG13317-null-fixture-purpose-v2'
    m = data.read_checked(path/'manifest.json','e3a2f4ba8d26b368328838e54db68be515dad20af72071d7b11c1862ef7aadd0')
    v = data.read_checked(path/'review.json',m['reviewSha256'])
    post = data.read_checked(data.BASE/'PG13318-null-fixture-purpose-post-v1/manifest.json','9cc205651a953ed3292b541957bfac90c2ee33b1c777e43f84e57726092183f0')
    assert post['actualExit'] == post['productTestsExecuted'] == post['newAccepted'] == 0 and post['independentOriginalIds'] == 4 and post['metadataNegativeVectors'] == 8
    assert post['reviewManifestSha256'] == data.sha((path/'manifest.json').read_bytes())
    assert v['source'] == post['source'] == '81a1b0c32be8167c07320e6bfaf469bcd44eb7bd'
    ids,refs,pending = previous_state();new = {r['id'] for r in v['rows']}
    assert len(new) == len(v['rows']) == 4 and new <= ids-refs
    assert all(r['manualPurposeReviewComplete'] is True and r['actualViolation'] is None and r['ptExecutionExempt'] is False for r in v['rows'])
    result = ids,refs|new,pending|new;assert [len(x) for x in result] == [7747,3349,1370]
    return result
